import os
import sys
import argparse
from dotenv import load_dotenv

# Ensure the project root is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.state import AgentState, BrandContext
from src.graph import create_brand_graph

load_dotenv(override=True)

def run_cli():
    parser = argparse.ArgumentParser(description="AuraBrand AI: Autonomous Brand Asset Generator")
    
    # Core Arguments
    parser.add_argument("--prompt", type=str, required=True, help="The mission description (e.g. 'Create a product pitch for a space pizza brand')")
    parser.add_argument("--intent", type=str, choices=["DOCUMENT", "PRESENTATION"], default="PRESENTATION", help="The type of asset to generate")
    
    # Brand Identity Arguments
    parser.add_argument("--brand", type=str, default="AuraBrand", help="The name of your brand")
    parser.add_argument("--tone", type=str, default="Innovative and professional", help="The desired brand tone")
    parser.add_argument("--color", type=str, default="#7C3AED", help="Primary brand color (hex)")
    parser.add_argument("--font", type=str, default="Fira Sans", help="Primary typography font family")
    
    # Control Arguments
    parser.add_argument("--iters", type=int, default=3, help="Max refinement iterations (default: 3)")
    parser.add_argument("--no-images", action="store_true", help="Disable AI image generation")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose node printing")

    args = parser.parse_args()

    # 1. Initialize the system
    app = create_brand_graph()
    
    # 2. Define the brand context from CLI or defaults
    brand = BrandContext(
        name=args.brand,
        tone=args.tone,
        primary_color=args.color,
        font_family=args.font,
        enable_images=not args.no_images,
        guidelines=f"Generated via AuraBrand CLI for {args.brand}. Mission: {args.prompt}"
    )
    
    # Combine intent with prompt
    full_prompt = f"I want to create a {args.intent.lower()}. {args.prompt}"
    
    initial_state: AgentState = {
        "user_request": full_prompt,
        "brand_context": brand,
        "current_draft": "",
        "research_notes": [],
        "feedback_history": [],
        "iteration_count": 0,
        "max_iterations": args.iters,
        "final_document": None,
        "output_files": []
    }
    
    # 3. Run the agentic loop
    print(f"\n Starting AuraBrand Mission: '{args.prompt}'")
    print(f"Intent: {args.intent} | Brand: {args.brand}")
    print("-" * 50)
    
    try:
        # We stream the steps
        for event in app.stream(initial_state):
            for node, state in event.items():
                if args.verbose:
                    print(f"   [Processing Node: {node}]")
                else:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                
                # Check for feedback nodes to report progress
                if node == "feedback" and state.get("feedback_history"):
                    last_feedback = state["feedback_history"][-1]
                    if args.verbose:
                        print(f"   - Compliance Score: {last_feedback.score:.2f}")
                        if last_feedback.suggestions:
                            print(f"   - Improvement Required: {last_feedback.suggestions[0]}")
        
        print("\n\n✅ Process Complete.")
        
        # Get final state from the stream result (simplified for CLI)
        # In a real graph we'd get the final state from the return of invoke/stream
        # but for now we'll just check the outputs directory.
        
        print(f"\n📂 Mission Deliverables generated.")
        print("-" * 50)
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()
