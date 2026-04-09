import json
import uuid
from typing import List
from langchain_core.messages import HumanMessage
from src.factory import get_model_with_fallback
from src.knowledge.brand_manager import BrandGuideline

def extract_brand_insights(text: str) -> List[BrandGuideline]:
    """Analyzes benchmark text to extract brand guidelines and patterns."""
    print("--- [Skill: Learn Agent] Analyzing benchmark text ---")
    
    model = get_model_with_fallback()
    
    # We take a sample or summary if the text is huge, but here we'll try to process the core
    # For very long docs, we'd chunk, but for benchmarks usually 5-20 pages is manageable
    text_sample = text[:15000] # Limit context to avoid token limits
    
    prompt = f"""
    You are the 'AuraBrand Analyst'. Your task is to reverse-engineer a brand's DNA from a benchmark document.
    
    BENCHMARK TEXT:
    {text_sample}
    
    TASK:
    Extract 3-5 concise, actionable brand guidelines from this text. 
    Focus on:
    1. Tone of Voice (e.g., 'Authoritative but accessible')
    2. Structural Patterns (e.g., 'Always leads with a problem statement')
    3. Terminology (e.g., 'Prefers "enable" over "allow"')
    
    FORMAT:
    Return a list of JSON objects, each with:
    - 'category': one of ['tone', 'structure', 'vocabulary']
    - 'content': The guideline text.
    
    Output ONLY valid JSON.
    """
    
    response = model.invoke([HumanMessage(content=prompt)])
    
    guidelines = []
    try:
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        for item in data:
            g_id = f"learned_{uuid.uuid4().hex[:8]}"
            guidelines.append(BrandGuideline(
                id=g_id,
                content=item['content'],
                category=item['category']
            ))
    except Exception as e:
        print(f"Error extracting insights: {e}")
        
    return guidelines
