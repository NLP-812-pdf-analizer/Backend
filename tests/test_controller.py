from ..controller.app import app
from fastapi.testclient import TestClient
import tempfile

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200

def test_uploading_files():
    with tempfile.NamedTemporaryFile(suffix=".txt") as file1, \
         tempfile.NamedTemporaryFile(suffix=".txt") as file2:
        files = [
        ("files", ("file1.txt", file1)),
        ("files", ("file2.txt", file2))
        ]   
        response = client.post("/api/graph", files=files)
        assert response.status_code == 200
        assert response.json() == {"received_files": ["file1.txt", "file2.txt"]}