# Text-Image-Protocol-TIP

**TIP (Text Image Protocol)** is an experimental image-to-text encoding format.

It converts image pixel data into a readable text representation.

## Features

- RGB image encoding
- Text-based pixel representation
- Configurable output dimensions
- Contain and stretch resize modes
- Python API
- Automated tests with pytest

## Installation

```bash
git clone https://github.com/EnderBrine03/Text-Image-Protocol-TIP.git

cd Text-Image-Protocol-TIP

pip install -r requirements.txt
```

### Usage

```python
from tip import encode_image

encode_image(
    "examples/test.png",
    "examples/output.tip",
    size=(64, 64),
    resize_mode="contain"
)
```

### Resize modes

| Mode    | Description                                  |
| ------- | -------------------------------------------- |
| contain | Preserves aspect ratio and centers the image |
| stretch | Resizes directly to the target dimensions    |

### TIP Format

Example:

```text
TIP/0.1
SIZE 2x2
COLOR_MODE RGB
COLOR_SPACE sRGB
DATA
FF0000 00FF00
0000FF FFFFFF
```

Each pixel is represented as a six-character hexadecimal RGB value.

### Testing

Run:

```bash
pytest -v
```

### Author

MageLordDev

### License

See the LICENSE file.
