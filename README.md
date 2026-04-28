# Image Inspector

A tool for inspecting and analyzing images.

## Project Structure

- `src/` – Source code
  - `main.py` – Main entry point
  - `metadata.py` – Metadata extraction utilities
  - `stego.py` – Steganography analysis
  - `utils.py` – Utility functions
- `output/` – Results directory
- `images/` – Test images directory
- `requirements.txt` – Python dependencies
- `.env` – Environment variables (not tracked)

## Getting Started

1. Create a virtual environment: `python -m venv venv`
2. Activate the environment and install dependencies: `pip install -r requirements.txt`
3. Run the application: `python src/main.py`

## Configuration

Copy the example environment variables from `.env.example` (if present) and fill in your values.
