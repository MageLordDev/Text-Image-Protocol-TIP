from tip import encode_image, decode_file


def main():
    input_path = "examples/test.png"
    output_path = "examples/test_v02.tip"
    decoded_path = "examples/decoded.png"

    try:
        encoded = encode_image(
            input_path=input_path,
            output_path=output_path,
            size=(64, 64),
            resize_mode="contain",
        )

        print("TIP/0.2 encoding completed!")
        print(f"Output: {output_path}")
        print(f"Characters: {len(encoded)}")

        decode_file(output_path, decoded_path)

        print("Decoding completed!")
        print(f"Decoded image: {decoded_path}")

    except FileNotFoundError:
        print(f"File not found: {input_path}")

    except Exception as error:
        print(f"Operation failed: {error}")


if __name__ == "__main__":
    main()
