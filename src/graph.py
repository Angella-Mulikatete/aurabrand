from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import creates_node, updates_skill_node, feedback_node

def should_continue(state: AgentState) -> str:
    """Decision logic to continue or stop the iteration."""
    # If the brand guardian is happy or we hit max iterations, we stop
    if state["iteration_count"] >= state["max_iterations"]:
        return "end"
    
    if state["feedback_history"] and state["feedback_history"][-1].is_compliant:
        return "end"
    
    return "creates"

def create_brand_graph():
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("creates", creates_node)
    workflow.add_node("updates_skill", updates_skill_node)
    workflow.add_node("feedback", feedback_node)

    # Define the flow
    workflow.set_entry_point("creates")
    
    # 1. First, create the draft
    workflow.add_edge("creates", "updates_skill")
    
    # 2. Second, update skills/research based on the creation
    workflow.add_edge("updates_skill", "feedback")
    
    # 3. Third, give feedback and decide if reviewed/complete
    workflow.add_conditional_edges(
        "feedback",
        should_continue,
        {
            "creates": "creates",
            "end": END
        }
    )
    
    return workflow.compile()

# Example usage
if __name__ == "__main__":
    app = create_brand_graph()
    print("Graph compiled successfully.")
