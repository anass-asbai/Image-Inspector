from PIL import Image


def extract_lsb(image_path):
    """
    Extract hidden message using LSB steganography.
    """

    img = Image.open(image_path)
    pixels = list(img.getdata())

    bits = ""

    # STEP 1: collect LSB from RGB
    for pixel in pixels:
        for color in pixel[:3]:  # R, G, B
            bits += str(color & 1)

    # STEP 2: convert bits → chars
    chars = []

    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]

        # stop condition (avoid garbage)
        if len(byte) < 8:
            break

        char = chr(int(byte, 2))

        chars.append(char)

    message = "".join(chars)

    return message