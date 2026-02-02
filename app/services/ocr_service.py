"""
OCR service layer using EasyOCR.
"""

import easyocr
from pathlib import Path
from typing import List

# English only
reader = easyocr.Reader(['en'], gpu=False)


def extract_text(image_path):
    """
    Args:
        image_path: Local path to the image file
    Returns:
        Extracted text
    Raises:
        FileNotFoundError: If the image file does not exist
        RuntimeError: If OCR processing fails for any other reason
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        # detail=0 returns only text strings
        # paragraph=True groups lines into logical paragraphs 
        results: List[str] = reader.readtext(
            str(path),
            detail=0,
            paragraph=True,
        )
        # Join paragraphs with double newline for clean separation
        return "\n\n".join(results).strip()
    except Exception as e:
        raise RuntimeError(f"OCR extraction failed: {str(e)}") from e




