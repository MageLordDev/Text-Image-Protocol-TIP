# Text-Image-Protocol-TIP

**TIP (Text Image Protocol)** is an experimental image-to-text encoding format designed to reduce text and tokenizer cost when representing images as plain text.

Current version: **0.2.0**

## Features

- Adaptive per-row encoding (RAW, RLE, PALETTE, REPEAT)
- Optional color quantization (lossy)
- Full encode + decode round-trip
- Configurable output dimensions and resize modes
- Python API
- Automated tests with pytest

## TIP/0.1 vs TIP/0.2

| | TIP/0.1 | TIP/0.2 |
|---|---------|---------|
| Header | `TIP/0.1` | `TIP/0.2` |
| Encoding | Always RAW hex pixels | Adaptive: RAW / RLE / PALETTE / REPEAT |
| Transform | none | `NONE` or `QUANTIZATION colors=N` |
| Decoder | not included | `decode_text` / `decode_file` |
| Typical size | larger | smaller on uniform/repeated content |

## Installation

```bash
git clone https://github.com/EnderBrine03/Text-Image-Protocol-TIP.git
cd Text-Image-Protocol-TIP
pip install -r requirements.txt
```

## Usage

### Encode

```python
from tip import encode_image

encoded = encode_image(
    "examples/test.png",
    "examples/output.tip",
    size=(64, 64),
    resize_mode="contain",
    quantize_colors=None,  # or 1..256 for lossy
)
```

### Decode

```python
from tip import decode_file, decode_text

decode_file("examples/output.tip", "examples/decoded.png")
image = decode_text(encoded)
```

### Resize modes

| Mode | Description |
|------|-------------|
| contain | Preserves aspect ratio and centers the image |
| stretch | Resizes directly to the target dimensions |

## TIP/0.2 Format

```text
TIP/0.2
SIZE 8x4
COLOR_MODE RGB
COLOR_SPACE sRGB
TRANSFORM NONE
OUTPUT_TYPE MIXED
DATA
ROW 1 RLE FFFFFF*8
ROW 2 PALETTE A=FFFFFF,B=FF0000 | A*2 B*4 A*2
ROW 3 REPEAT
ROW 4 RAW FFFFFF FFFFFF ...
```

### Encoding methods

- **RAW** — six-character RGB hex per pixel
- **RLE** — run-length encoding (`COLOR*count`)
- **PALETTE** — short symbols mapped to colors
- **REPEAT** — copy previous row

The encoder chooses the shortest representation for each row independently.

### Quantization

`quantize_colors=N` reduces the image to at most N colors (lossy). Header becomes:

```text
TRANSFORM QUANTIZATION colors=N
```

## Testing

```bash
pytest -v
```

## Author

MageLordDev

## License

See the LICENSE file.
