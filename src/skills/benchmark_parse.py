from pypdf import PdfReader
from docx import Document
import io

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extracts text from a PDF byte stream."""
    try:
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def extract_text_from_docx(file_content: bytes) -> str:
    """Extracts text from a DOCX byte stream."""
    try:
        doc = Document(io.BytesIO(file_content))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""

def parse_benchmark(filename: str, content: bytes) -> str:
    """Dispatcher to parse benchmarks based on extension."""
    ext = filename.split(".")[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(content)
    elif ext == "docx":
        return extract_text_from_docx(content)
    elif ext == "txt":
        return content.decode("utf-8", errors="ignore")
    else:
        print(f"Unsupported benchmark format: {ext}")
        return ""
