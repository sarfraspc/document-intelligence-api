"""
Tests for the ask endpoint.
"""


def test_ask_question_valid(client, uploaded_document_id):
    payload = {
        "document_id": uploaded_document_id,
        "question": "What is the total amount?",
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"].strip()) > 0  


def test_ask_invalid_document_id(client):
    payload = {
        "document_id": 99999,  
        "question": "What is the date?",
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 404