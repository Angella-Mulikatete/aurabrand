from typing import Annotated, List, TypedDict, Union
from pydantic import BaseModel, Field

class BrandContext(BaseModel):
    name: str = "Default"
    guidelines: str = ""
    tone: str = "Neutral"
    forbidden_terms: List[str] = Field(default_factory=list)

class Feedback(BaseModel):
    is_compliant: bool
    suggestions: List[str]
    score: float  # 0 to 1

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
