import fitz  # PyMuPDF
import pdfplumber
import base64
import io


def extract_text_pymupdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def extract_text_plumber(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()


def pdf_to_base64_images(pdf_path: str) -> list:
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, dpi=200)
        encoded = []
        for img in images:
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            encoded.append(base64.b64encode(buffer.getvalue()).decode())
        return encoded
    except Exception as e:
        print(f"Vision fallback unavailable: {e}")
        return []


def extract_pdf(pdf_path: str) -> tuple:
    """Returns (text, is_scanned)."""
    text = extract_text_pymupdf(pdf_path)
    if len(text) < 100:
        text = extract_text_plumber(pdf_path)
    if len(text) < 100:
        return "", True
    return text, False
