from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def convert_to_degrees(value):
    d = value[0][0] / value[0][1]
    m = value[1][0] / value[1][1]
    s = value[2][0] / value[2][1]

    return d + (m / 60.0) + (s / 3600.0)


def get_gps_info(exif_data):
    gps_data = {}

    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id)

        if tag == "GPSInfo":
            for key in value:
                name = GPSTAGS.get(key)
                gps_data[name] = value[key]

    if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
        lat = convert_to_degrees(gps_data["GPSLatitude"])
        lon = convert_to_degrees(gps_data["GPSLongitude"])

        return {"latitude": lat, "longitude": lon}

    return None


def extract_metadata(image_path):
    try:
        img = Image.open(image_path)
        exif = img._getexif()

        if not exif:
            return {"error": "No metadata found"}

        data = {}

        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)

            if tag == "Make":
                data["device_make"] = value
            elif tag == "Model":
                data["device_model"] = value
            elif tag == "DateTime":
                data["date"] = value

        gps = get_gps_info(exif)

        if gps:
            data["gps"] = gps

        return data

    except Exception as e:
        return {"error": str(e)}