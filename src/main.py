import argparse
from metadata import extract_metadata

def main():
    parser = argparse.ArgumentParser(description="Image Inspector (test metadata)")

    parser.add_argument("-m", "--metadata", action="store_true", help="Extract metadata")
    parser.add_argument("image", help="Path to image")

    args = parser.parse_args()

    if args.metadata:
        result = extract_metadata(args.image)
        print(result)
    else:
        print("Use -m to extract metadata")


if __name__ == "__main__":
    main()