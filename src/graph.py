from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import drafting_node, review_node, improvement_node

def should_continue(state: AgentState) -> str:
    """Decision logic to continue or stop the iteration."""
    # If the brand guardian is happy or we hit max iterations, we stop
    if state["iteration_count"] >= state["max_iterations"]:
        return "end"
    
    if state["feedback_history"] and state["feedback_history"][-1].is_compliant:
        return "end"
    
    return "improve"

def create_brand_graph():
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("drafting", drafting_node)
    workflow.add_node("review", review_node)
    workflow.add_node("improvement", improvement_node)

    # Define the flow
    workflow.set_entry_point("drafting")
    
    workflow.add_edge("drafting", "review")
    
    # Conditional edge from review
    workflow.add_conditional_edges(
        "review",
        should_continue,
        {
            "improve": "improvement",
            "end": END
        }
    )
    
    workflow.add_edge("improvement", "drafting")

    return workflow.compile()

# Example usage
if __name__ == "__main__":
    app = create_brand_graph()
    print("Graph compiled successfully.")
