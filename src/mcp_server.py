import os
import sys
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Ensure the project root is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import AgentState, BrandContext
from src.graph import create_brand_graph
from src.knowledge.brand_manager import BrandManager

# Initialize FastMCP server
mcp = FastMCP("AuraBrand")

@mcp.tool()
async def aurabrand_generate(
    prompt: str,
    intent: str = "PRESENTATION",
    brand_name: str = "AuraBrand",
    tone: str = "Innovative and professional",
    primary_color: str = "#7C3AED",
    font_family: str = "Fira Sans",
    enable_images: bool = True
) -> str:
    """
    Generates high-fidelity brand assets (DOCX, PPTX, PDF) based on a mission prompt and brand identity.
    Args:
        prompt: The description of what you want to create.
        intent: Either 'PRESENTATION' or 'DOCUMENT'.
        brand_name: The name of the brand.
        tone: The desired brand tone.
        primary_color: Primary hex color.
        font_family: Typography brand choice.
        enable_images: Whether to generate AI visuals for the content.
    """
    app = create_brand_graph()
    
    brand = BrandContext(
        name=brand_name,
        tone=tone,
        primary_color=primary_color,
        font_family=font_family,
        enable_images=enable_images,
        guidelines=f"Generated via AuraBrand MCP for {brand_name}."
    )
    
    full_prompt = f"I want to create a {intent.lower()}. {prompt}"
    
    initial_state: AgentState = {
        "user_request": full_prompt,
        "brand_context": brand,
        "current_draft": "",
        "research_notes": [],
        "feedback_history": [],
        "iteration_count": 0,
        "max_iterations": 3,
        "final_document": None,
        "output_files": []
    }
    
    # Run the graph (invoke is better for MCP than stream)
    final_state = app.invoke(initial_state)
    
    deliverables = "\n".join([f"- {os.path.basename(f)}" for f in final_state.get("output_files", [])])
    
    return f"### AuraBrand Mission Complete\n\n**Generated Assets:**\n{deliverables}\n\n**Final Document Draft:**\n\n{final_state.get('final_document', 'No draft text generated.')}"

@mcp.resource("brand://guidelines")
def get_brand_guidelines() -> str:
    """Lists current learned brand guidelines and patterns."""
    bm = BrandManager()
    stats = bm.get_knowledge_stats()
    return f"AuraBrand Knowledge Stats:\n- Total Learned Patterns: {stats.get('total')}\n- Category Breakdown: {stats.get('categories')}"

@mcp.resource("brand://visuals")
def get_brand_visuals() -> str:
    """Retrieves current visual brand identity (colors, fonts)."""
    bm = BrandManager()
    visuals = bm.get_visuals()
    return f"AuraBrand Visual Identity:\n{visuals}"

if __name__ == "__main__":
    mcp.run()
