import os
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from src.state import AgentState, Feedback
from src.skills.research import research_skill
from src.factory import get_model

load_dotenv()

def drafting_node(state: AgentState) -> AgentState:
    """The Strategist and Wordsmith collaborate to create or update the draft."""
    print("--- [Node: Drafting] ---")
    
    # Initialize the model dynamically
    model = get_model()
    
    # Gather context
    brand_identity = state["brand_context"].guidelines
    last_feedback = ""
    if state["feedback_history"]:
        last_feedback = f"Past Feedback: {state['feedback_history'][-1].suggestions}"

    prompt = f"""
    You are the 'AuraBrand Wordsmith'. Your goal is to create high-quality content that feels native to the brand.
    
    BRAND GUIDELINES:
    {brand_identity}
    
    USER REQUEST:
    {state['user_request']}
    
    RESEARCH NOTES:
    {state['research_notes']}
    
    {last_feedback}
    
    Current Draft:
    {state.get('current_draft', 'None')}
    
    Task: Update/Create the draft. Ensure it is better than the previous version and addresses all feedback.
    Output only the refined content.
    """
    
    response = model.invoke([HumanMessage(content=prompt)])
    
    # Update state
    return {
        **state,
        "current_draft": response.content,
        "iteration_count": state["iteration_count"] + 1
    }

def review_node(state: AgentState) -> AgentState:
    """The Brand Guardian reviews the draft against brand guidelines."""
    print("--- [Node: Review] ---")
    
    model = get_model()
    draft = state["current_draft"]
    brand_context = state["brand_context"]
    
    prompt = f"""
    You are the 'AuraBrand Guardian'. You are strict, detailed, and obsessed with brand consistency.
    
    BRAND CONTEXT:
    Tone: {brand_context.tone}
    Forbidden Terms: {brand_context.forbidden_terms}
    General Guidelines: {brand_context.guidelines}
    
    DRAFT TO REVIEW:
    {draft}
    
    Review this draft. Is it compliant? What needs improvement?
    Format your response as a JSON object with:
    'is_compliant': bool,
    'suggestions': [list of strings],
    'score': float (0-1)
    """
    
    response = model.invoke([HumanMessage(content=prompt)])
    
    try:
        # Strip potential markdown code blocks
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        feedback = Feedback(**data)
    except:
        feedback = Feedback(is_compliant=False, suggestions=["Error parsing feedback. Re-review required."], score=0.0)
    
    return {
        **state,
        "feedback_history": state["feedback_history"] + [feedback]
    }

def improvement_node(state: AgentState) -> AgentState:
    """The Evaluator synthesizes feedback and research to guide the next iteration."""
    print("--- [Node: Improvement] ---")
    
    # The Evaluator might decide we need more research
    query = state["user_request"]
    new_facts = research_skill(query, depth=state["iteration_count"])
    
    return {
        **state,
        "research_notes": state["research_notes"] + new_facts
    }
