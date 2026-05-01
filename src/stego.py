import numpy as np
from PIL import Image
from pathlib import Path


def extract_lsb(image_path: str, sentinel: bytes = b"\x00") -> str:
    """
    Extract a hidden message from an image using LSB steganography.
    Stops at the first null byte (sentinel) to avoid garbage output.
    """
    if not Path(image_path).is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(image_path) as img:
        arr = np.array(img.convert("RGB"))

    lsb_bits = (arr[:, :, :3] & 1).flatten()

    if len(lsb_bits) < 8:
        raise ValueError("Image too small to contain a hidden message.")

    byte_array = np.packbits(lsb_bits).tobytes()
    message_bytes = byte_array.split(sentinel)[0]

    return message_bytes.decode("utf-8", errors="replace")


def detect_pgp(text: str) -> str:
    """Detect if extracted text contains a PGP block."""
    if "-----BEGIN PGP MESSAGE-----" in text:
        return "[!] PGP encrypted message detected."
    return "[✓] No PGP signature found."