from tip import encode_image


def main():
    encode_image(
        "examples/test.png",
        "examples/test.tip",
        size=(64, 64),
        resize_mode="contain"
    )

    print("TIP encoding completed successfully.")


if __name__ == "__main__":
    main()
