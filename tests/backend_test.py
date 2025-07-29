from controller.main import app
from fastapi.testclient import TestClient
import tempfile

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200

def test_uploading_files():
    with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
        # Готовим payload для отправки. Ключ словаря files_payload должен
        # совпадать с именем аргумента в эндпоинте.
        files_payload = {'pdfFile': ('test.pdf', pdf_file, 'application/pdf')}
        response = client.post("/api/graph", files=files_payload)
        assert response.status_code == 200
        assert response.json() == {"received_file": "test.pdf"}