from src.skills.doc_gen import generate_docx
from src.skills.pdf_gen import generate_pdf
from src.skills.pptx_gen import generate_pptx
from src.state import BrandContext
import os

def test_asset_pack():
    brand = BrandContext(name="AuraBrand", guidelines="Simple", tone="Professional")
    content = """
    AuraBrand Document Ecosystem
    
    This is a professional announcement regarding our latest innovations.
    Key points:
    - AI-Driven
    - Human-Centric
    - Sustainable
    """
    
    base = "outputs/verify_full"
    
    # 🧪 Test Generations
    results = [
        generate_docx(content, brand, f"{base}.docx"),
        generate_pdf(content, brand, f"{base}.pdf"),
        generate_pptx(content, brand, f"{base}.pptx")
    ]
    
    for r in results:
        if os.path.exists(r):
            print(f"Created: {os.path.basename(r)}")
        else:
            print(f"Failed: {os.path.basename(r)}")

if __name__ == "__main__":
    test_asset_pack()
