from PIL import Image
import numpy as np


def encode_image(
    input_path,
    output_path=None,
    size=(64, 64),
    resize_mode="contain"
):
    if resize_mode not in ("contain", "stretch"):
        raise ValueError("Invalid resize mode")

    if (
        not isinstance(size, (tuple, list))
        or len(size) != 2
        or any(
            not isinstance(v, int) or isinstance(v, bool) or v <= 0
            for v in size
        )
    ):
        raise ValueError("Size must contain two positive integers")

    with Image.open(input_path) as source:
        image = source.convert("RGB")

        if resize_mode == "stretch":
            image = image.resize(
                tuple(size),
                Image.Resampling.LANCZOS
            )
        else:
            image.thumbnail(
                tuple(size),
                Image.Resampling.LANCZOS
            )

            canvas = Image.new("RGB", tuple(size), (0, 0, 0))

            x = (size[0] - image.width) // 2
            y = (size[1] - image.height) // 2

            canvas.paste(image, (x, y))
            image = canvas

        pixels = np.asarray(image, dtype=np.uint8)

    height, width, _ = pixels.shape

    lines = [
        "TIP/0.1",
        f"SIZE {width}x{height}",
        "COLOR_MODE RGB",
        "COLOR_SPACE sRGB",
        "DATA"
    ]

    for row in pixels:
        lines.append(
            " ".join(
                f"{r:02X}{g:02X}{b:02X}"
                for r, g, b in row
            )
        )

    encoded = "\n".join(lines) + "\n"

    if output_path:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(encoded)

    return encoded
