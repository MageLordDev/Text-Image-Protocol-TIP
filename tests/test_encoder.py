import pytest

from PIL import Image

from tip import encode_image


def create_test_image(path, size=(10, 10), color=(255, 0, 0)):
    image = Image.new("RGB", size, color)
    image.save(path)


def test_png_encoding(tmp_path):
    input_path = tmp_path / "test.png"
    output_path = tmp_path / "test.tip"

    create_test_image(input_path)

    result = encode_image(
        input_path,
        output_path,
        size=(64, 64)
    )

    assert result.startswith("TIP/0.1")
    assert output_path.exists()


def test_pixel_count(tmp_path):
    input_path = tmp_path / "test.png"

    create_test_image(input_path)

    result = encode_image(
        input_path,
        size=(8, 8),
        resize_mode="stretch"
    )

    lines = result.splitlines()

    assert lines[1] == "SIZE 8x8"

    pixel_lines = lines[5:]

    assert len(pixel_lines) == 8

    for line in pixel_lines:
        assert len(line.split()) == 8


def test_invalid_image():
    with pytest.raises(FileNotFoundError):
        encode_image("this_file_does_not_exist.png")


def test_invalid_resize_mode(tmp_path):
    input_path = tmp_path / "test.png"

    create_test_image(input_path)

    with pytest.raises(ValueError):
        encode_image(
            input_path,
            resize_mode="invalid"
        )
