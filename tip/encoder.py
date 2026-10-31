from pathlib import Path
import re

from PIL import Image


TIP_VERSION = "TIP/0.2"

PALETTE_SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def _validate_size(size):
    if (
        not isinstance(size, (tuple, list))
        or len(size) != 2
        or any(
            not isinstance(v, int) or isinstance(v, bool) or v <= 0
            for v in size
        )
    ):
        raise ValueError("Size must contain two positive integers")


def _hex(pixel):
    return "{:02X}{:02X}{:02X}".format(*pixel)


def _parse_hex(value):
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", value):
        raise ValueError(f"Invalid RGB color: {value}")
    return tuple(bytes.fromhex(value))


def _rle_encode(row):
    result = []
    i = 0
    while i < len(row):
        color = row[i]
        count = 1
        while i + count < len(row) and row[i + count] == color:
            count += 1
        result.append(f"{_hex(color)}*{count}")
        i += count
    return " ".join(result)


def _palette_encode(row):
    colors = list(dict.fromkeys(row))
    if len(colors) > len(PALETTE_SYMBOLS):
        return None
    palette = {color: PALETTE_SYMBOLS[index] for index, color in enumerate(colors)}
    definition = ",".join(f"{symbol}={_hex(color)}" for color, symbol in palette.items())
    encoded = " ".join(palette[color] for color in row)
    return f"{definition} | {encoded}"


def _encode_row(index, row, previous_row):
    if previous_row is not None and row == previous_row:
        return f"ROW {index} REPEAT"

    raw = " ".join(_hex(pixel) for pixel in row)
    rle = _rle_encode(row)
    palette = _palette_encode(row)

    candidates = [
        (f"ROW {index} RAW {raw}", "RAW"),
        (f"ROW {index} RLE {rle}", "RLE"),
    ]
    if palette is not None:
        candidates.append((f"ROW {index} PALETTE {palette}", "PALETTE"))

    return min(candidates, key=lambda item: len(item[0]))[0]


def encode_image(
    input_path,
    output_path=None,
    size=(64, 64),
    resize_mode="contain",
    quantize_colors=None,
):
    """Encode an image using TIP/0.2."""
    _validate_size(size)

    if resize_mode not in ("contain", "stretch"):
        raise ValueError("Invalid resize mode")

    if quantize_colors is not None:
        if (
            not isinstance(quantize_colors, int)
            or isinstance(quantize_colors, bool)
            or not 1 <= quantize_colors <= 256
        ):
            raise ValueError("quantize_colors must be between 1 and 256")

    with Image.open(input_path) as source:
        image = source.convert("RGB")

        if resize_mode == "stretch":
            image = image.resize(tuple(size), Image.Resampling.LANCZOS)
        else:
            image.thumbnail(tuple(size), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", tuple(size), (0, 0, 0))
            x = (size[0] - image.width) // 2
            y = (size[1] - image.height) // 2
            canvas.paste(image, (x, y))
            image = canvas

        if quantize_colors is not None:
            image = image.quantize(
                colors=quantize_colors,
                method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE,
            ).convert("RGB")

        width, height = image.size
        px = image.load()
        pixels = [px[x, y] for y in range(height) for x in range(width)]

    transform = "NONE" if quantize_colors is None else f"QUANTIZATION colors={quantize_colors}"

    lines = [
        TIP_VERSION,
        f"SIZE {width}x{height}",
        "COLOR_MODE RGB",
        "COLOR_SPACE sRGB",
        f"TRANSFORM {transform}",
        "OUTPUT_TYPE MIXED",
        "DATA",
    ]

    previous_row = None
    for y in range(height):
        start = y * width
        row = pixels[start:start + width]
        lines.append(_encode_row(y + 1, row, previous_row))
        previous_row = row

    encoded = "\n".join(lines) + "\n"

    if output_path is not None:
        Path(output_path).write_text(encoded, encoding="utf-8")

    return encoded


def decode_text(content):
    """Decode a TIP/0.2 string into a PIL RGB image."""
    if not isinstance(content, str):
        raise TypeError("TIP content must be a string")

    lines = content.splitlines()

    if len(lines) < 8 or lines[0] != TIP_VERSION:
        raise ValueError("Unsupported or invalid TIP version")

    size_match = re.fullmatch(r"SIZE (\d+)x(\d+)", lines[1])
    if not size_match:
        raise ValueError("Invalid SIZE header")

    width, height = map(int, size_match.groups())
    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive")

    if lines[2] != "COLOR_MODE RGB":
        raise ValueError("Unsupported color mode")
    if lines[3] != "COLOR_SPACE sRGB":
        raise ValueError("Unsupported color space")
    if not lines[4].startswith("TRANSFORM "):
        raise ValueError("Missing TRANSFORM header")
    if not lines[5].startswith("OUTPUT_TYPE "):
        raise ValueError("Missing OUTPUT_TYPE header")
    if lines[6] != "DATA":
        raise ValueError("Missing DATA marker")

    data_lines = lines[7:]
    if len(data_lines) != height:
        raise ValueError(f"Expected {height} rows, got {len(data_lines)}")

    decoded_rows = []

    for expected_index, line in enumerate(data_lines, start=1):
        parts = line.split(" ", 3)

        if len(parts) < 3 or parts[0] != "ROW":
            raise ValueError(f"Invalid row {expected_index}")

        try:
            row_index = int(parts[1])
        except ValueError as exc:
            raise ValueError("Invalid row index") from exc

        if row_index != expected_index:
            raise ValueError("Rows must be in sequential order")

        mode = parts[2]

        if mode == "REPEAT":
            if len(parts) != 3 or not decoded_rows:
                raise ValueError("Invalid REPEAT row")
            row = decoded_rows[-1][:]
        else:
            if len(parts) != 4:
                raise ValueError(f"Missing row data at row {row_index}")
            payload = parts[3]

            if mode == "RAW":
                row = [_parse_hex(token) for token in payload.split()]
            elif mode == "RLE":
                row = []
                for token in payload.split():
                    match = re.fullmatch(r"([0-9A-Fa-f]{6})\*(\d+)", token)
                    if not match:
                        raise ValueError("Invalid RLE token")
                    color = _parse_hex(match.group(1))
                    count = int(match.group(2))
                    if count <= 0:
                        raise ValueError("RLE count must be positive")
                    if len(row) + count > width:
                        raise ValueError("RLE row exceeds image width")
                    row.extend([color] * count)
            elif mode == "PALETTE":
                if " | " not in payload:
                    raise ValueError("Invalid PALETTE row")
                definition, encoded = payload.split(" | ", 1)
                palette = {}
                for item in definition.split(","):
                    if "=" not in item:
                        raise ValueError("Invalid palette definition")
                    symbol, color = item.split("=", 1)
                    if (
                        len(symbol) != 1
                        or symbol not in PALETTE_SYMBOLS
                        or symbol in palette
                    ):
                        raise ValueError("Invalid palette symbol")
                    palette[symbol] = _parse_hex(color)
                row = []
                for symbol in encoded.split():
                    if symbol not in palette:
                        raise ValueError("Unknown palette symbol")
                    row.append(palette[symbol])
            else:
                raise ValueError(f"Unsupported row type: {mode}")

        if len(row) != width:
            raise ValueError(f"Row {row_index} has {len(row)} pixels; expected {width}")

        decoded_rows.append(row)

    flat_pixels = [pixel for row in decoded_rows for pixel in row]
    image = Image.new("RGB", (width, height))
    image.putdata(flat_pixels)
    return image


def decode_file(input_path, output_path):
    """Decode a TIP/0.2 file and save it as PNG."""
    content = Path(input_path).read_text(encoding="utf-8")
    image = decode_text(content)
    image.save(output_path, format="PNG")
    return image
