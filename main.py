import argparse
import json
import os

from src.metadata import extract_metadata
from src.stego import extract_lsb, detect_pgp


def format_output(result: dict) -> str:
    """Format metadata result for human-readable output."""
    lines = []

    if "gps" in result:
        lat = result["gps"]["latitude"]
        lon = result["gps"]["longitude"]
        lines.append(f"Lat/Lon: ({lat}) / ({lon})")

    if "device_make" in result and "device_model" in result:
        lines.append(f"Device: {result['device_make']} {result['device_model']}")
    elif "device_model" in result:
        lines.append(f"Device: {result['device_model']}")

    if "date" in result:
        lines.append(f"Date: {result['date']}")

    return "\n".join(lines)


def save_output(content: str, output_path: str) -> None:
    """Write content to file and confirm."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Data saved in {os.path.basename(output_path)}")


def main():
    parser = argparse.ArgumentParser(description="Image Inspector")
    parser.add_argument("-m", "--metadata", action="store_true", help="Extract metadata")
    parser.add_argument("-s", "--stego",    action="store_true", help="Detect steganography")
    parser.add_argument("-o", "--output",   help="Output file path")
    parser.add_argument("image",            help="Path to image")

    args = parser.parse_args()

    # Single file check lives here — stego.py no longer needs its own
    if not os.path.isfile(args.image):
        print(json.dumps({"error": "File does not exist"}, indent=2))
        return

    # ---------------- METADATA MODE ----------------
    if args.metadata:
        try:
            result = extract_metadata(args.image)
            output_text = format_output(result)
        except Exception as e:
            print(json.dumps({"error": f"Metadata extraction failed: {e}"}, indent=2))
            return

        if args.output:
            save_output(output_text, args.output)
        else:
            print(output_text)

    # ---------------- STEGO MODE ----------------
    elif args.stego:
        try:
            hidden = extract_lsb(args.image)
        except ValueError as e:
            print(json.dumps({"error": str(e)}, indent=2))
            return
        except Exception as e:
            print(json.dumps({"error": f"LSB extraction failed: {e}"}, indent=2))
            return

        pgp_status = detect_pgp(hidden)
        final_output = f"{hidden}\n\n{pgp_status}"

        if args.output:
            save_output(final_output, args.output)
        else:
            print(final_output)

    else:
        print("Use -m for metadata or -s for steganography. Use -h for help.")


if __name__ == "__main__":
    main()