# класс-обертка пдф в текст 

from pypdf import PdfReader


class PdfTextConverterService:
    def __init__(self):
        pass

    def convert_pdf_to_text(self, pdf_content: bytes) -> str:
        # This is a placeholder for actual PDF to text conversion logic
        # In a real application, you would use a library like PyPDF2 or pdfminer.six
        return f"Text extracted from PDF with content length: {len(pdf_content)}"