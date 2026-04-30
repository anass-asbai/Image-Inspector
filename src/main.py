import argparse
import json
import os
from metadata import extract_metadata


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
    parser.add_argument("-m", "--metadata", action="store_true", help="Extract metadata")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("image", help="Path to image")
    args = parser.parse_args()

    if not os.path.isfile(args.image):
        print(json.dumps({"error": "File does not exist"}, indent=2))
        return

    if args.metadata:
        result = extract_metadata(args.image)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(format_output(result))
            print(f"Data saved in {os.path.basename(args.output)}")
        else:
            print(format_output(result))
    else:
        print("Use -m to extract metadata")


if __name__ == "__main__":
    main()
