import os
from pptx import Presentation
from pptx.util import Inches, Pt
from src.state import BrandContext

def generate_pptx(content: str, brand: BrandContext, output_path: str = "output.pptx") -> str:
    """
    Generates a brand-compliant PPTX presentation.
    Splits content into slides based on double newlines or bullet-heavy sections.
    """
    prs = Presentation()

    # 1. Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text = brand.name
    subtitle.text = f"Agentic Content Strategy: {brand.tone}"

    # 2. Split Content into Slides
    # We look for main sections or break long content
    sections = [s.strip() for s in content.split("\n\n") if s.strip()]
    
    bullet_slide_layout = prs.slide_layouts[1]

    for section in sections:
        # If the section is short, create a title/content slide
        lines = section.split("\n")
        slide = prs.slides.add_slide(bullet_slide_layout)
        
        # Use the first line as slide title if it's short, otherwise generic
        if len(lines[0]) < 50:
            slide.shapes.title.text = lines[0]
            body_text = "\n".join(lines[1:])
        else:
            slide.shapes.title.text = "Key Insight"
            body_text = section
            
        tf = slide.placeholders[1].text_frame
        tf.text = body_text
        
        # Apply basic brand-aware font sizing
        for p in tf.paragraphs:
            p.font.size = Pt(18)

    # 3. Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    
    print(f"✅ PPTX generated at: {output_path}")
    return os.path.abspath(output_path)
