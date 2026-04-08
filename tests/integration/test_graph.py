import pytest
from unittest.mock import patch, MagicMock
from src.graph import create_brand_graph
from src.state import AgentState, BrandContext, Feedback

@pytest.fixture
def mock_brand_context():
    return BrandContext(
        name="TestBrand",
        guidelines="Be professional.",
        tone="Professional",
        forbidden_terms=["bad"]
    )

@patch("src.nodes.get_model_with_fallback")
@patch("src.nodes.research_skill")
def test_full_graph_flow(mock_research, mock_get_model, mock_brand_context):
    """
    Test the full graph flow: Start -> Creates -> Updates Skill -> Feedback -> Reviewed.
    """
    app = create_brand_graph()
    
    # Mock behavior: 
    # 1. Creates returns a draft
    # 2. Updates Skill does research
    # 3. Feedback returns is_compliant=True
    mock_model = MagicMock()
    mock_model.invoke.side_effect = [
        MagicMock(content="Mocked Draft"), # Creates node
        MagicMock(content='{"is_compliant": true, "suggestions": [], "score": 1.0}') # Feedback node
    ]
    mock_get_model.return_value = mock_model
    mock_research.return_value = ["Skill Update Fact"]
    
    initial_state = {
        "user_request": "Write a greeting.",
        "brand_context": mock_brand_context,
        "current_draft": "",
        "research_notes": [],
        "feedback_history": [],
        "iteration_count": 0,
        "max_iterations": 3,
        "final_document": None
    }
    
    final_state = app.invoke(initial_state)
    
    assert final_state["current_draft"] == "Mocked Draft"
    assert "Skill Update Fact" in final_state["research_notes"]
    assert len(final_state["feedback_history"]) == 1
    assert final_state["feedback_history"][-1].is_compliant is True
    assert final_state["iteration_count"] == 1
