from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

"""
Shared pytest fixtures for API testing.
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont 

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def dummy_image_bytes():
    """Generate a small in-memory PNG image with visible text"""
    # Create white background
    img = Image.new("RGB", (400, 200), color="white")
    draw = ImageDraw.Draw(img)
    
    # Use default font 
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw sample invoice text
    text = (
        "Sample Invoice\n"
        "Total Amount: $391.00\n"
        "Date: January 15, 2024\n"
        "Vendor: Example Corp\n"
        "Item: Widget - $300.00\n"
        "Tax: $91.00"
    )
    draw.text((20, 20), text, fill="black", font=font)
    
    byte_io = BytesIO()
    img.save(byte_io, format="PNG")
    byte_io.seek(0)
    return byte_io


@pytest.fixture
def uploaded_document_id(client, dummy_image_bytes):
    """Upload the dummy image and return the document_id."""
    response = client.post(
        "/upload",
        files={"file": ("test_invoice.png", dummy_image_bytes, "image/png")},
    )
    assert response.status_code == 201
    return response.json()["document_id"]