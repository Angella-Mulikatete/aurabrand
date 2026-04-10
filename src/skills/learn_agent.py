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

def extract_edit_insights(original: str, final: str) -> List[BrandGuideline]:
    """Analyzes the differences between an AI draft and a user's manual edit to extract brand guidelines."""
    print("--- [Skill: Learn Agent] Analyzing Manual Edits ---")
    
    model = get_model_with_fallback()
    
    prompt = f"""
    You are the 'AuraBrand Analyst'. Compare an AI-generated draft to the user's final manually edited version.
    Identify WHAT the user changed, and extract 1 to 3 concise, actionable brand guidelines based on those edits.
    
    ORIGINAL AI DRAFT:
    {original}
    
    FINAL USER EDITED DRAFT:
    {final}
    
    Focus on changes in:
    1. Tone of Voice
    2. Specific Terminology or Vocabulary (e.g. avoided words vs preferred words)
    3. Formatting or Structure
    
    Return a JSON array of objects with:
    - 'category': one of ['tone', 'structure', 'vocabulary']
    - 'content': The guideline text.
    
    If there are no meaningful stylistic changes, return an empty array [].
    Output ONLY valid JSON.
    """
    
    response = model.invoke([HumanMessage(content=prompt)])
    
    guidelines = []
    try:
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        for item in data:
            g_id = f"learned_edit_{uuid.uuid4().hex[:8]}"
            guidelines.append(BrandGuideline(
                id=g_id,
                content=item['content'],
                category=item['category']
            ))
    except Exception as e:
        print(f"Error extracting edit insights: {e}")
        
    return guidelines
