import pytest
from PIL import Image

from tip import encode_image, decode_text, decode_file


def create_image(path, size=(8, 8)):
    image = Image.new("RGB", size)
    pixels = []
    for y in range(size[1]):
        for x in range(size[0]):
            if y < 4:
                pixels.append((255, 255, 255))
            else:
                pixels.append((255, 0, 0) if x < 4 else (0, 0, 255))
    image.putdata(pixels)
    image.save(path)


def test_tip_v02_header(tmp_path):
    source = tmp_path / "source.png"
    create_image(source)
    result = encode_image(source, size=(8, 8), resize_mode="stretch")
    assert result.startswith("TIP/0.2\n")
    assert "OUTPUT_TYPE MIXED" in result


def test_round_trip_lossless(tmp_path):
    source = tmp_path / "source.png"
    create_image(source)
    encoded = encode_image(source, size=(8, 8), resize_mode="stretch")
    decoded = decode_text(encoded)
    with Image.open(source) as original:
        original = original.convert("RGB")
    assert [
        decoded.getpixel((x, y))
        for y in range(decoded.height)
        for x in range(decoded.width)
    ] == [
        original.getpixel((x, y))
        for y in range(original.height)
        for x in range(original.width)
    ]


def test_rle_encoding(tmp_path):
    source = tmp_path / "test_rle.png"
    Image.new("RGB", (8, 1), (255, 255, 255)).save(source)
    encoded = encode_image(source, size=(8, 1), resize_mode="stretch")
    assert "ROW 1 RLE FFFFFF*8" in encoded


def test_repeat_row(tmp_path):
    source = tmp_path / "repeat.png"
    Image.new("RGB", (8, 3), (255, 255, 255)).save(source)
    encoded = encode_image(source, size=(8, 3), resize_mode="stretch")
    assert "ROW 2 REPEAT" in encoded
    assert "ROW 3 REPEAT" in encoded


def test_quantization_header(tmp_path):
    source = tmp_path / "source.png"
    create_image(source)
    encoded = encode_image(source, size=(8, 8), resize_mode="stretch", quantize_colors=2)
    assert "TRANSFORM QUANTIZATION colors=2" in encoded


def test_invalid_quantization(tmp_path):
    source = tmp_path / "source.png"
    create_image(source)
    with pytest.raises(ValueError):
        encode_image(source, quantize_colors=0)


def test_invalid_file():
    with pytest.raises(FileNotFoundError):
        encode_image("missing_image.png")


def test_decode_file(tmp_path):
    source = tmp_path / "source.png"
    tip_file = tmp_path / "output.tip"
    decoded_file = tmp_path / "decoded.png"
    create_image(source)
    encode_image(source, tip_file, size=(8, 8), resize_mode="stretch")
    decode_file(tip_file, decoded_file)
    assert decoded_file.exists()
    with Image.open(decoded_file) as image:
        assert image.size == (8, 8)
