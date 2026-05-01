# 🔍 Image Inspector

> A Python-based digital forensics tool for extracting EXIF metadata and detecting LSB steganography in images.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-10.x-blue?style=flat-square)
![NumPy](https://img.shields.io/badge/NumPy-1.x-013243?style=flat-square&logo=numpy)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Domain](https://img.shields.io/badge/Domain-Digital%20Forensics-red?style=flat-square)

---

## 📌 Overview

**Image Inspector** is a command-line digital forensics tool designed for cybersecurity analysts and students. It performs two core investigative operations on image files:

- **Metadata Forensics** — extracts embedded EXIF data such as GPS location, device identity, and timestamps from JPEG/PNG images.
- **Steganography Detection** — uncovers hidden messages embedded inside image pixels using the Least Significant Bit (LSB) technique, and flags PGP-encrypted payloads.

This tool is suitable for CTF challenges, digital forensics investigations, OSINT workflows, and academic research in image analysis.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📍 GPS Extraction | Converts raw EXIF GPS IFD data to decimal latitude/longitude |
| 📷 Device Identification | Reads camera make and model from EXIF tags |
| 📅 Timestamp Recovery | Extracts `DateTimeOriginal` or `DateTime` from image metadata |
| 🕵️ LSB Steganography | Reconstructs hidden text from pixel-level LSB encoding |
| 🔐 PGP Detection | Detects `-----BEGIN PGP MESSAGE-----` blocks in extracted data |
| 💾 File Output | Saves any result to a specified output file |
| 🛡️ Clean Error Handling | Structured JSON errors — no raw tracebacks exposed |

---

## 🗂️ Project Structure

```
image-inspector/
│
├── main.py          # CLI entry point — argument parsing and mode routing
├── stego.py         # LSB extraction engine + PGP block detection
├── metadata.py      # EXIF metadata extraction and GPS parsing
└── README.md
```

---

## ⚙️ How It Works

### 1. EXIF Metadata Extraction

EXIF (Exchangeable Image File Format) is a standard that embeds metadata inside image files at the time of capture. This metadata is stored in structured binary tags and can include:

- **GPS coordinates** stored as Degrees/Minutes/Seconds (DMS) rationals in the `GPSInfo` IFD (Image File Directory)
- **Device identity** stored under EXIF tags `Make` (tag `0x010F`) and `Model` (tag `0x0110`)
- **Timestamps** stored under `DateTimeOriginal` (tag `0x9003`) or `DateTime` (tag `0x0132`)

**Extraction pipeline:**

```
Image file
    └── Pillow getexif()
            └── Raw tag IDs → TAGS/GPSTAGS lookup
                    └── GPS: DMS → Decimal conversion
                    └── Date: "2023:07:20" → "2023-07-20" normalisation
                    └── Output dict → CLI or file
```

GPS decimal conversion formula:
```
Decimal Degrees = Degrees + (Minutes / 60) + (Seconds / 3600)
```
South latitudes and West longitudes are negated accordingly.

---

### 2. LSB Steganography Detection

LSB steganography hides data by replacing the **least significant bit** of each color channel (R, G, B) in every pixel. Since flipping the LSB changes a pixel value by only ±1, the modification is imperceptible to the human eye.

**Extraction pipeline:**

```
Image file
    └── numpy array (H × W × 3)
            └── Bitwise AND with 1 → isolates LSB of each channel
                    └── np.packbits() → reconstructs bytes
                            └── Split on \x00 sentinel → message boundary
                                    └── UTF-8 decode → readable text
                                            └── PGP header scan → flag if found
```

**Why NumPy?** Using `np.packbits()` over the pixel array is significantly faster than looping byte-by-byte, and avoids per-character string allocations on large images.

**Sentinel termination:** The encoder is expected to append a null byte (`\x00`) after the message. The extractor splits on this byte to isolate the payload from the remaining pixel noise.

---

## 🛠️ Installation

### Prerequisites

- Python **3.8** or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourname/image-inspector.git
cd image-inspector

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install pillow numpy
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `Pillow` | Image loading, EXIF/IFD parsing |
| `NumPy` | Vectorized LSB extraction via bitwise ops |

---

## 🚀 Usage

### Syntax

```bash
python main.py [MODE] [-o OUTPUT] <image>
```

### Flags

| Flag | Long form | Description |
|------|-----------|-------------|
| `-m` | `--metadata` | Extract EXIF metadata |
| `-s` | `--stego` | Detect LSB steganography |
| `-o` | `--output` | Save output to a file |
| `-h` | `--help` | Display help message |

---

### Examples

**Extract and print metadata:**
```bash
python main.py -m photo.jpg
```

**Extract metadata and save to file:**
```bash
python main.py -m photo.jpg -o report.txt
```

**Scan image for hidden LSB message:**
```bash
python main.py -s suspicious.png
```

**Scan and save steganography result:**
```bash
python main.py -s suspicious.png -o extracted.txt
```

---

### Sample Output

**Metadata mode (`-m`):**
```
Lat/Lon: (48.858600) / (2.352200)
Device: Apple iPhone 14 Pro
Date: 2024-03-15 14:22:10
```

**Steganography mode (`-s`) — clean image:**
```
No readable message found.

[✓] No PGP signature found.
```

**Steganography mode (`-s`) — image with hidden payload:**
```
This message was hidden inside the image pixels.

[!] PGP encrypted message detected.
```

**Error output (JSON format):**
```json
{
  "error": "File does not exist"
}
```

---

## 🔒 Ethical & Legal Considerations

> **This tool is intended for authorized use only.**

Image Inspector is developed for **educational**, **research**, and **authorized forensic investigation** purposes. Using this tool without proper authorization may violate applicable laws.

### ✅ Permitted Use

- Analyzing images **you own** or have **explicit written permission** to inspect
- CTF (Capture The Flag) competitions and cybersecurity lab exercises
- Academic research and coursework in digital forensics
- Authorized OSINT investigations and penetration testing engagements

### ❌ Prohibited Use

- Extracting personal or private information from images **without consent**
- Identifying individuals via GPS metadata for **surveillance or stalking**
- Analyzing images obtained through **unauthorized access**
- Any use that violates local, national, or international law including **GDPR**, **CFAA** (USA), or **Computer Misuse Act** (UK)

### ⚠️ Privacy Notice

GPS metadata embedded in photos can reveal sensitive locations such as a person's home, workplace, or daily routine. Always handle extracted metadata responsibly and in accordance with applicable privacy regulations.

---

## 🧪 Testing

To verify the tool works correctly, test with a known image:

```bash
# Metadata test — use any JPEG taken with a phone
python main.py -m test_image.jpg

# Steganography test — embed a message first with an LSB encoder, then extract
python main.py -s stego_image.png
```

If EXIF data is missing (e.g., screenshots, web images), you will receive:
```json
{
  "error": "No EXIF metadata found"
}
```

---

## 📋 Limitations

- LSB extraction only succeeds if the image was encoded with a **compatible LSB encoder** using a `\x00` terminator
- EXIF data is often **stripped by social media platforms** (Twitter, Instagram, WhatsApp) before upload
- PNG images rarely contain GPS EXIF; **JPEG is the most reliable format** for metadata
- Only single-image input is supported per run; batch processing is not yet implemented

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for full terms.

---

## 👤 Author

Developed as part of a cybersecurity portfolio focused on digital forensics and image analysis.

> *"The image shows more than what the eye can see."*