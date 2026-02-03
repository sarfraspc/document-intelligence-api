"""
OCR service layer using tesseract
"""

import pytesseract
from pathlib import Path
from PIL import Image

def extract_text(image_path):
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        img = Image.open(path)
        config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, lang='eng', config=config)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"OCR extraction failed: {str(e)}") from e




