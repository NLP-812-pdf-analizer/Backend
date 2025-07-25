# here to get pdfs and return their texts in json
# ручка на запрос с заглушкой-классом получения текста в жсон

from fastapi import FastAPI, UploadFile
from pypdf import PdfReader
from io import BytesIO

app = FastAPI()

@app.post("/pdf_to_graph")
async def pdf_to_graph(received_pdf : UploadFile) -> dict[str,str]:
    pdf_bytes = await received_pdf.read()

    pdf_stream = BytesIO(pdf_bytes)
    reader = PdfReader(pdf_stream)

    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()

    single_line = " ".join(full_text.split())

    data = {"pdf_text": single_line}

    return data