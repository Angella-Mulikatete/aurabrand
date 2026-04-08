import pytest
from unittest.mock import patch, MagicMock
from src.state import AgentState, BrandContext, Feedback
from src.nodes import creates_node, feedback_node, updates_skill_node

@pytest.fixture
def mock_brand_context():
    return BrandContext(
        name="TestBrand",
        guidelines="Be professional.",
        tone="Professional",
        forbidden_terms=["bad"]
    )

@pytest.fixture
def initial_state(mock_brand_context):
    return {
        "user_request": "Write a greeting.",
        "brand_context": mock_brand_context,
        "current_draft": "",
        "research_notes": [],
        "feedback_history": [],
        "iteration_count": 0,
        "max_iterations": 3,
        "final_document": None
    }

@patch("src.nodes.get_model_with_fallback")
def test_creates_node(mock_get_model, initial_state):
    # Mock the model's response
    mock_model = MagicMock()
    mock_model.invoke.return_value.content = "Hello from the creates node!"
    mock_get_model.return_value = mock_model
    
    new_state = creates_node(initial_state)
    
    assert new_state["current_draft"] == "Hello from the creates node!"
    assert new_state["iteration_count"] == 1

@patch("src.nodes.get_model_with_fallback")
def test_feedback_node_success(mock_get_model, initial_state):
    # Mock the model's response as JSON
    mock_model = MagicMock()
    mock_model.invoke.return_value.content = '{"is_compliant": true, "suggestions": [], "score": 1.0}'
    mock_get_model.return_value = mock_model
    
    initial_state["current_draft"] = "Test draft"
    new_state = feedback_node(initial_state)
    
    assert len(new_state["feedback_history"]) == 1
    assert new_state["feedback_history"][-1].is_compliant is True
    assert new_state["feedback_history"][-1].score == 1.0

@patch("src.nodes.research_skill")
def test_updates_skill_node(mock_research, initial_state):
    # Mock research result
    mock_research.return_value = ["Fact 1", "Fact 2"]
    
    new_state = updates_skill_node(initial_state)
    
    assert "Fact 1" in new_state["research_notes"]
    assert len(new_state["research_notes"]) == 2
