from PIL import Image
import numpy as np


def encode_image(
    input_path,
    output_path=None,
    size=(64, 64),
    resize_mode="contain"
):
    """
    Encode an image into the TIP text-based format.

    Args:
        input_path: Source image path.
        output_path: Optional output .tip file path.
        size: Target image dimensions (width, height).
        resize_mode: 'contain' or 'stretch'.

    Returns:
        str: Encoded TIP text.
    """

    if resize_mode not in ("contain", "stretch"):
        raise ValueError(
            "resize_mode must be 'contain' or 'stretch'"
        )

    with Image.open(input_path) as image:
        image = image.convert("RGB")

        if resize_mode == "stretch":
            image = image.resize(size, Image.Resampling.LANCZOS)

        else:
            image.thumbnail(size, Image.Resampling.LANCZOS)

            canvas = Image.new("RGB", size, (0, 0, 0))

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

    encoded = "\n".join(lines)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(encoded)

    return encoded
