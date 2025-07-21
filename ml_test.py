import io
from fastapi.testclient import TestClient

from model.main import ml

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

client = TestClient(ml)

def test_pdf_to_graph_endpoint():
    test_text = "This is a test PDF"
    
    pdf_buffer = io.BytesIO()

    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    c.drawString(100, 750, test_text)
    c.save()

    pdf_buffer.seek(0)

    files = {'received_pdf': ('test.pdf', pdf_buffer, 'application/pdf')}

    response = client.post("/pdf_to_graph", files=files)

    assert response.status_code == 200
    expected_json = {"pdf_text": test_text}
    assert response.json() == expected_json