from tip import encode_image

encode_image(
    "examples/test.png",
    "examples/test.tip",
    size=(64, 64),
    resize_mode="contain"
)
