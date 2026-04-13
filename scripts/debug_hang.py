import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import(module_name, import_stmt):
    print(f"Testing {module_name}...")
    t0 = time.time()
    try:
        exec(import_stmt)
        print(f"OK: {module_name} ({time.time() - t0:.2f}s)")
    except Exception as e:
        print(f"FAILED: {module_name} - {str(e)}")

test_import("os, json, re", "import os, json, re")
test_import("dotenv", "from dotenv import load_dotenv")
test_import("langchain_core", "from langchain_core.messages import HumanMessage")
test_import("src.state", "from src.state import AgentState, Feedback")
test_import("src.skills.research", "from src.skills.research import research_skill")
test_import("src.skills.doc_gen", "from src.skills.doc_gen import generate_docx")
test_import("src.skills.pdf_gen", "from src.skills.pdf_gen import generate_pdf")
test_import("src.skills.pptx_gen", "from src.skills.pptx_gen import generate_pptx")
test_import("src.skills.image_gen", "from src.skills.image_gen import generate_image")
test_import("src.factory", "from src.factory import get_model, get_model_with_fallback")
test_import("src.knowledge.brand_manager", "from src.knowledge.brand_manager import BrandManager, BrandGuideline")
test_import("src.graph", "from src.graph import create_brand_graph")

print("All imports tested.")
