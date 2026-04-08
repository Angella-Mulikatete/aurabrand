import os
from dotenv import load_dotenv
from src.state import AgentState, BrandContext
from src.graph import create_brand_graph

load_dotenv()

def main():
    # 1. Initialize the system
    app = create_brand_graph()
    
    # 2. Define the starting context
    brand = BrandContext(
        name="AuraBrand",
        guidelines="""
        AuraBrand is a premium, innovative, and human-centric technology brand.
        We avoid robotic language. We use metaphors that feel organic.
        We always focus on 'Empowerment' rather than 'Efficiency'.
        """,
        tone="Inspirational but grounded",
        forbidden_terms=["synergy", "low-hanging fruit", "paradigm shift"]
    )
    
    initial_state: AgentState = {
        "user_request": "Write a short announcement for our new AI-driven document ecosystem.",
        "brand_context": brand,
        "current_draft": "",
        "research_notes": [],
        "feedback_history": [],
        "iteration_count": 0,
        "max_iterations": 3,
        "final_document": None
    }
    
    # 3. Run the agentic loop
    print("Starting BrandWise AutoDoc Loop...")
    
    # We can stream the steps
    for event in app.stream(initial_state):
        for node, state in event.items():
            print(f"\n--- Node '{node}' completed ---")
            if "current_draft" in state:
                print(f"Current Draft Snippet: {state['current_draft'][:100]}...")
            if "feedback_history" in state and state["feedback_history"]:
                last_feedback = state["feedback_history"][-1]
                print(f"Compliance Score: {last_feedback.score}")
                print(f"Suggestions: {last_feedback.suggestions}")

    print("\n Process Complete.")

if __name__ == "__main__":
    main()
