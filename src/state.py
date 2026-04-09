from typing import Annotated, List, TypedDict, Union
from pydantic import BaseModel, Field

class BrandContext(BaseModel):
    name: str = "Default"
    guidelines: str = ""
    tone: str = "Neutral"
    forbidden_terms: List[str] = Field(default_factory=list)
    
    # Visual Identity (V2)
    primary_color: str = "#7d33ff" # Default purple
    secondary_color: str = "#ffffff"
    font_family: str = "Arial"
    logo_url: Union[str, None] = None

class Feedback(BaseModel):
    is_compliant: bool
    suggestions: List[str]
    score: float  # Overall score 0 to 1
    # Dimensional breakdown (Tone, Visual, Structure)
    breakdown: dict = Field(default_factory=lambda: {"tone": 0.0, "visual": 0.0, "structure": 0.0})

class AgentState(TypedDict):
    # Input
    user_request: str
    brand_context: BrandContext
    
    # Internal Working Data
    current_draft: str
    research_notes: List[str]
    feedback_history: List[Feedback]
    
    # Iteration Control
    iteration_count: int
    max_iterations: int
    
    # Final Output
    final_document: Union[str, None]
    output_files: List[str] # Paths to generated .docx, .pdf, etc.
