"""
Tests for the upload endpoint.
"""


def test_upload_valid_image(client, dummy_image_bytes):
    response = client.post(
        "/upload",
        files={"file": ("valid_test.png", dummy_image_bytes, "image/png")},
    )
    assert response.status_code == 201
    data = response.json()
    assert "document_id" in data
    assert isinstance(data["document_id"], int)
    assert data["filename"] == "valid_test.png"


def test_upload_invalid_file_type(client):
    # Upload as text file
    response = client.post(
        "/upload",
        files={"file": ("invalid.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]