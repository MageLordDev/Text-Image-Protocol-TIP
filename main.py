from tip import encode_image


def main():
    input_path = "examples/test.png"
    output_path = "examples/test.txt"

    try:
        encoded = encode_image(
            input_path=input_path,
            output_path=output_path,
            size=(64, 64),
            resize_mode="contain"
        )

        print("TIP encoding completed!")
        print(f"Output: {output_path}")
        print(f"Characters: {len(encoded)}")

    except FileNotFoundError:
        print(f"Image not found: {input_path}")

    except Exception as error:
        print(f"Encoding failed: {error}")


if __name__ == "__main__":
    main()
