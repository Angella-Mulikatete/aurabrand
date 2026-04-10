from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os

from src.graph import create_brand_graph
from src.state import BrandContext, AgentState
from src.knowledge.brand_manager import BrandManager, BrandGuideline
from src.skills.benchmark_parse import parse_benchmark
from src.skills.learn_agent import extract_brand_insights

app = FastAPI(title="AuraBrand AI API")

# Serve generated outputs as static files for downloads
os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Configure CORS so the Next.js frontend can make requests (Allowing all local dev ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using our hardcoded brand for now until full DB pass-through is implemented in Phase 4
brand = BrandContext(
    name="AuraBrand",
    tone="innovative, professional, forward-thinking",
    guidelines="Avoid jargon. Use short sentences. Highlight human empowerment.",
    forbidden_terms=["synergy", "paradigm", "leverage"],
    primary_color="#7C3AED",
)

class GenerateRequest(BaseModel):
    user_request: str
    intent: str = "PRESENTATION" # PRESENTATION or DOCUMENT
    brand_name: Optional[str] = "AuraBrand"
    primary_color: Optional[str] = "#7C3AED"
    font_family: Optional[str] = "Arial"
    enable_images: Optional[bool] = True

class GenerateResponse(BaseModel):
    output_files: List[str]
    final_document: Optional[str]

class RefineRequest(BaseModel):
    feedback: str
    previous_document: str
    intent: str = "PRESENTATION" # PRESENTATION or DOCUMENT
    brand_name: Optional[str] = "AuraBrand"
    primary_color: Optional[str] = "#7C3AED"
    font_family: Optional[str] = "Arial"
    enable_images: Optional[bool] = True

@app.post("/generate", response_model=GenerateResponse)
async def generate_brand_assets(req: GenerateRequest):
    try:
        brand_graph = create_brand_graph()
        
        # Build dynamic BrandContext based on user selection
        user_brand = BrandContext(
            name=req.brand_name or "AuraBrand",
            tone="innovative, professional, forward-thinking",
            guidelines="Avoid jargon. Use short sentences. Highlight human empowerment.",
            forbidden_terms=["synergy", "paradigm", "leverage"],
            primary_color=req.primary_color or "#7C3AED",
            font_family=req.font_family or "Arial",
            enable_images=req.enable_images if req.enable_images is not None else True
        )
        
        # Format the user request to include intent for the agent
        prompt_with_intent = f"I want to create a {req.intent.lower()}. {req.user_request}"
        
        initial_state: AgentState = {
            "user_request": prompt_with_intent,
            "brand_context": user_brand,
            "current_draft": "",
            "research_notes": [],
            "feedback_history": [],
            "iteration_count": 0,
            "max_iterations": 3,
            "final_document": None,
            "output_files": []
        }
        
        print(f"Triggering AuraBrand LangGraph for request: '{req.user_request}'")
        final_state = brand_graph.invoke(initial_state)
        
        return GenerateResponse(
            output_files=final_state["output_files"],
            final_document=final_state["final_document"]
        )
        
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine", response_model=GenerateResponse)
async def refine_brand_assets(req: RefineRequest):
    try:
        brand_graph = create_brand_graph()
        
        user_brand = BrandContext(
            name=req.brand_name or "AuraBrand",
            tone="innovative, professional, forward-thinking",
            guidelines="Avoid jargon. Use short sentences. Highlight human empowerment.",
            forbidden_terms=["synergy", "paradigm", "leverage"],
            primary_color=req.primary_color or "#7C3AED",
            font_family=req.font_family or "Arial",
            enable_images=req.enable_images if req.enable_images is not None else True
        )
        
        prompt_with_intent = f"Please improve the existing {req.intent.lower()} based on this feedback: {req.feedback}"
        
        initial_state: AgentState = {
            "user_request": prompt_with_intent,
            "brand_context": user_brand,
            "current_draft": req.previous_document,
            "research_notes": [],
            "feedback_history": [],
            "iteration_count": 0,
            "max_iterations": 3,
            "final_document": None,
            "output_files": []
        }
        
        print(f"Triggering AuraBrand LangGraph refinement for: '{req.feedback}'")
        final_state = brand_graph.invoke(initial_state)
        
        return GenerateResponse(
            output_files=final_state["output_files"],
            final_document=final_state["final_document"]
        )
        
    except Exception as e:
        print(f"Error during refinement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/benchmarks/upload")
async def upload_benchmarks(files: List[UploadFile] = File(...)):
    """Uploads benchmark docs and learns from them."""
    bm = BrandManager()
    results = []
    
    print(f"--- [API: Benchmarks] Starting upload of {len(files)} files ---")
    
    for file in files:
        try:
            print(f"Processing file: {file.filename}")
            content = await file.read()
            text = parse_benchmark(file.filename, content)
            
            if not text:
                print(f"Warning: No text extracted from {file.filename}")
                continue
            
            print(f"Extracted {len(text)} characters. Running Learn Agent...")
            # Extract brand insights using the Learn Agent
            insights = extract_brand_insights(text)
            
            print(f"Extracted {len(insights)} brand insights.")
            # Save insights to the Knowledge Base (BrandManager)
            for insight in insights:
                bm.add_guideline(insight)
            
            results.append({
                "filename": file.filename,
                "insights_count": len(insights),
                "status": "success"
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": f"error: {str(e)}"
            })
            
    return {"results": results, "total_learned": bm.get_count()}

@app.post("/benchmarks/reset")
async def reset_benchmarks():
    """Clears all learned benchmark knowledge."""
    bm = BrandManager()
    bm.clear_brand_data()
    return {"status": "success", "message": "Brand knowledge reset."}

if __name__ == "__main__":
    import uvicorn
    # Make sure we load env vars first
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    print("Starting AuraBrand API Server on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
