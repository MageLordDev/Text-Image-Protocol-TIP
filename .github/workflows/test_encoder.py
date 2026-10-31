
from PIL import Image
from tip import encode_image


def test_png_encoding(tmp_path):
    image_path = tmp_path / "test.png"
    output_path = tmp_path / "test.tip"

    Image.new("RGB", (100, 100), (255, 0, 0)).save(image_path)

    result = encode_image(str(image_path), str(output_path))

    assert result.startswith("TIP/0.1")
    assert "SIZE:64x64" in result
    assert output_path.exists()


def test_pixel_count(tmp_path):
    image_path = tmp_path / "test.png"
    Image.new("RGB", (100, 100), (255, 0, 0)).save(image_path)

    result = encode_image(str(image_path))
    data = result.split("DATA:\n", 1)[1]
    rows = data.splitlines()

    assert len(rows) == 64

    for row in rows:
        assert len(row.split(",")) == 64


def test_invalid_image():
    try:
        encode_image("this_file_does_not_exist.png")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("FileNotFoundError bekleniyordu")
      
