from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _rational_to_float(value) -> float | None:
    """Convert a rational, tuple, or numeric value to float."""
    try:
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            return value.numerator / value.denominator
        if isinstance(value, (tuple, list)) and len(value) == 2:
            return value[0] / value[1]
        return float(value)
    except (TypeError, ZeroDivisionError, ValueError):
        return None


def _dms_to_decimal(dms) -> float | None:
    """Convert (degrees, minutes, seconds) GPS tuple to decimal degrees."""
    try:
        d, m, s = (_rational_to_float(dms[i]) for i in range(3))
        if None in (d, m, s):
            return None
        return d + (m / 60.0) + (s / 3600.0)
    except (IndexError, TypeError):
        return None


def _format_date(raw: str) -> str:
    """Normalise EXIF date '2023:07:20 14:32:10' → '2023-07-20 14:32:10'."""
    return raw.replace(":", "-", 2)


# ---------------------------------------------------------------------------
# GPS extraction
# ---------------------------------------------------------------------------

def _get_raw_gps_ifd(exif) -> dict | None:
    """Return the raw GPS IFD dict from any Pillow EXIF object shape."""
    if hasattr(exif, "get_ifd"):
        gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
        if gps:
            return gps
    if raw := exif.get(34853):
        return raw
    if isinstance(exif, dict):
        return next(
            (v for k, v in exif.items() if TAGS.get(k) == "GPSInfo"),
            None,
        )
    return None


def extract_gps(exif) -> dict | None:
    """
    Return {"latitude": float, "longitude": float} in decimal degrees,
    or None if GPS data is absent or malformed.
    """
    raw = _get_raw_gps_ifd(exif)
    if not raw:
        return None

    gps = {GPSTAGS.get(k, k): v for k, v in raw.items()}

    lat_dms = gps.get("GPSLatitude")
    lon_dms = gps.get("GPSLongitude")
    if not (lat_dms and lon_dms):
        return None

    lat = _dms_to_decimal(lat_dms)
    lon = _dms_to_decimal(lon_dms)
    if lat is None or lon is None:
        return None

    if gps.get("GPSLatitudeRef") == "S":
        lat = -lat
    if gps.get("GPSLongitudeRef") == "W":
        lon = -lon

    return {"latitude": round(lat, 6), "longitude": round(lon, 6)}


# ---------------------------------------------------------------------------
# EXIF extraction
# ---------------------------------------------------------------------------

def _load_exif(img: Image.Image):
    """Return the EXIF object from a Pillow image, or None."""
    if hasattr(img, "getexif"):
        exif = img.getexif()
        if exif:
            return exif
    if hasattr(img, "_getexif"):
        return img._getexif()
    return None


def extract_metadata(image_path: str) -> dict:
    """
    Open *image_path* and return a flat metadata dict:

        {
            "device_make":  str | absent,
            "device_model": str | absent,
            "date":         str | absent,   # normalised to YYYY-MM-DD HH:MM:SS
            "gps":          {"latitude": float, "longitude": float} | absent,
        }

    On any failure the dict contains a single "error" key.
    """
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        return {"error": f"File not found: {image_path}"}
    except OSError as exc:
        return {"error": f"Cannot open image: {exc}"}

    exif = _load_exif(img)
    if not exif:
        return {"error": "No EXIF metadata found"}

    # Tags we care about: EXIF name → output key (dates handled separately)
    FIELD_MAP = {"Make": "device_make", "Model": "device_model"}
    DATE_TAGS = ("DateTimeOriginal", "DateTime")   # priority order

    data: dict = {}
    dates: dict = {}

    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag in FIELD_MAP:
            data[FIELD_MAP[tag]] = str(value).strip().rstrip("\x00")
        elif tag in DATE_TAGS and tag not in dates:
            dates[tag] = str(value)

    # Pick the most precise date available
    raw_date = dates.get("DateTimeOriginal") or dates.get("DateTime")
    if raw_date:
        data["date"] = _format_date(raw_date)

    gps = extract_gps(exif)
    if gps:
        data["gps"] = gps

    return data