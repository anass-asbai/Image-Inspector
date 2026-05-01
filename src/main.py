import argparse
import json
import os

from metadata import extract_metadata
from stego import extract_lsb, detect_pgp


def format_output(result):
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


def main():
    parser = argparse.ArgumentParser(description="Image Inspector")

    # metadata mode
    parser.add_argument("-m", "--metadata", action="store_true", help="Extract metadata")

    # stego mode (NEW)
    parser.add_argument("-s", "--stego", action="store_true", help="Detect steganography")

    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("image", help="Path to image")

    args = parser.parse_args()

    # check file exists
    if not os.path.isfile(args.image):
        print(json.dumps({"error": "File does not exist"}, indent=2))
        return

    # ---------------- METADATA MODE ----------------
    if args.metadata:
        result = extract_metadata(args.image)

        output_text = format_output(result)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output_text)
            print(f"Data saved in {os.path.basename(args.output)}")
        else:
            print(output_text)

    # ---------------- STEGO MODE ----------------
    elif args.stego:
        hidden = extract_lsb(args.image)

        pgp_status = detect_pgp(hidden)

        final_output = hidden + "\n\n" + pgp_status

        if args.output:
            with open(args.output, "w") as f:
                f.write(final_output)
            print(f"Data saved in {os.path.basename(args.output)}")
        else:
            print(final_output)

    else:
        print("Use -m (metadata) or -s (steganography)")


if __name__ == "__main__":
    main()