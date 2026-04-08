import os
from dotenv import load_dotenv
from src.state import AgentState, BrandContext
from src.graph import create_brand_graph

load_dotenv(override=True)

def run_brand_eval():
    """
    Evaluation script to verify the 'self-improving' aspect of the agent.
    It seeds the system with a non-compliant draft and ensures it improves.
    """
    app = create_brand_graph()
    
    brand = BrandContext(
        name="AuraBrand",
        guidelines="""
        AuraBrand is premium, human-centric, and organic. 
        Forbidden: jargon, robotic language, 'synergy', 'efficiency'.
        Focus on: 'Empowerment', 'Connection'.
        """,
        tone="Inspirational but grounded",
        forbidden_terms=["synergy", "efficiency", "low-hanging fruit"]
    )
    
    # Starting with a 'bad' draft that uses forbidden terms and robotic language
    bad_draft = "Our AI system increases efficiency and creates synergy for low-hanging fruit."
    
    state: AgentState = {
        "user_request": "Update the announcement to reflect our core brand values.",
        "brand_context": brand,
        "current_draft": bad_draft,
        "research_notes": [],
        "feedback_history": [],
        "iteration_count": 0,
        "max_iterations": 2,
        "final_document": None
    }
    
    print(f"Starting Evaluation with Initial Draft: {bad_draft}")
    
    results = []
    # Running the full graph
    for event in app.stream(state):
        for node, s in event.items():
            if "feedback_history" in s and s["feedback_history"]:
                last_score = s["feedback_history"][-1].score
                print(f"--- Iteration Completed ---")
                print(f"Node: {node}")
                print(f"Current Draft: {s.get('current_draft', '')[:100]}...")
                print(f"Compliance Score: {last_score}")
                results.append(last_score)

    if len(results) > 1:
        initial_score = results[0]
        final_score = results[-1]
        print(f"\nFinal Eval Result:")
        print(f"Initial Score: {initial_score} -> Final Score: {final_score}")
        if final_score > initial_score:
            print("✅ SUCCESS: The agent self-improved.")
        elif final_score == 1.0:
            print("✅ SUCCESS: The agent reached full compliance.")
        else:
            print("⚠️ WARNING: The agent did not improve its score significantly.")
    else:
        print("Evaluation finished in one step or failed to produce history.")

if __name__ == "__main__":
    run_brand_eval()
