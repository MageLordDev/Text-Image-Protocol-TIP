from tip import encode_image

encode_image(
    "examples/test.jpg",
    "examples/test.tip",
    size=(64, 64),
    resize_mode="contain"
)
