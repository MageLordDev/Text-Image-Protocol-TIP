
"""
TIP Encoder
Converts image files into Text Image Protocol (TIP) data.
"""

from pathlib import Path
from PIL import Image
import numpy as np


def encode_image(
    image_path: str,
    output_path: str = None,
    size: tuple = (64, 64),
    resize_mode: str = "contain"
) -> str:
    """
    Convert an image into TIP text format.

    Args:
        image_path: Source image path.
        output_path: Optional output .tip file.
        size: Output dimensions (width, height).
        resize_mode: 'contain' or 'stretch'.

    Returns:
        Encoded TIP text.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if resize_mode not in ("contain", "stretch"):
        raise ValueError("resize_mode must be 'contain' or 'stretch'")

    width, height = size

    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive")

    with Image.open(image_path) as source:
        image = source.convert("RGB")

        if resize_mode == "stretch":
            image = image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )
        else:
            image.thumbnail(
                (width, height),
                Image.Resampling.LANCZOS
            )

            canvas = Image.new("RGB", (width, height), (0, 0, 0))

            x = (width - image.width) // 2
            y = (height - image.height) // 2

            canvas.paste(image, (x, y))
            image = canvas

        pixels = np.asarray(image, dtype=np.uint8)

    rows = []

    for row in pixels:
        encoded_row = [
            f"#{r:02X}{g:02X}{b:02X}"
            for r, g, b in row
        ]
        rows.append(",".join(encoded_row))

    tip_data = (
        "TIP/0.1\n"
        f"SIZE:{width}x{height}\n"
        "COLOR_MODE:HEX\n"
        "COLOR_SPACE:RGB\n"
        "DATA:\n"
        + "\n".join(rows)
    )

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(tip_data, encoding="utf-8")

    return tip_data
  
