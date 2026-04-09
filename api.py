from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os

from src.graph import create_brand_graph
from src.state import BrandContext, AgentState

app = FastAPI(title="AuraBrand AI API")

# Serve generated outputs as static files for downloads
os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Configure CORS so the Next.js frontend can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

class GenerateResponse(BaseModel):
    output_files: List[str]
    final_document: Optional[str]

@app.post("/generate", response_model=GenerateResponse)
async def generate_brand_assets(req: GenerateRequest):
    try:
        brand_graph = create_brand_graph()
        
        # Format the user request to include intent for the agent
        # The agent relies on detecting this word in nodes.py detect_intent
        prompt_with_intent = f"I want to create a {req.intent.lower()}. {req.user_request}"
        
        initial_state: AgentState = {
            "user_request": prompt_with_intent,
            "brand_context": brand,
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

if __name__ == "__main__":
    import uvicorn
    # Make sure we load env vars first
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    print("Starting AuraBrand API Server on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
