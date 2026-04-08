import os
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from src.state import AgentState, Feedback
from src.skills.research import research_skill
from src.skills.doc_gen import generate_docx
from src.skills.pdf_gen import generate_pdf
from src.skills.pptx_gen import generate_pptx
from src.factory import get_model, get_model_with_fallback
from src.knowledge.brand_manager import BrandManager, BrandGuideline

load_dotenv()

def creates_node(state: AgentState) -> AgentState:
    """The agent CREATES the initial or updated draft."""
    print("--- [Node: Creates] ---")
    
    # Initialize the model dynamically (with automatic fallback)
    model = get_model_with_fallback()
    
    # Retrieve relevant brand guidelines from memory
    bm = BrandManager()
    memory_guidelines = bm.get_guidelines(state["user_request"])
    memory_context = "\n".join([f"- {g}" for g in memory_guidelines])
    
    # Gather context
    brand_identity = state["brand_context"].guidelines
    last_feedback = ""
    if state["feedback_history"]:
        last_feedback = f"Past Feedback: {state['feedback_history'][-1].suggestions}"

    prompt = f"""
    You are the 'AuraBrand Wordsmith'. Your goal is to create high-quality content that feels native to the brand.
    
    CORE BRAND GUIDELINES:
    {brand_identity}
    
    PAST LEARNED LESSONS & RELEVANT MEMORY:
    {memory_context if memory_context else "No specific past lessons found for this topic yet."}
    
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
    updated_state = {
        **state,
        "current_draft": response.content,
        "iteration_count": state["iteration_count"] + 1
    }

    # Final Step: If we are at the end, generate all formats
    if updated_state["iteration_count"] >= state["max_iterations"]:
        # 📂 Create Asset Pack paths
        base_path = f"outputs/brand_run_{state['iteration_count']}"
        docx_path = f"{base_path}.docx"
        pdf_path = f"{base_path}.pdf"
        pptx_path = f"{base_path}.pptx"
        
        # 🪄 Generate Files
        docx_url = generate_docx(response.content, state["brand_context"], docx_path)
        pdf_url = generate_pdf(response.content, state["brand_context"], pdf_path)
        pptx_url = generate_pptx(response.content, state["brand_context"], pptx_path)
        
        updated_state["output_files"] = [docx_url, pdf_url, pptx_url]
        updated_state["final_document"] = response.content

    return updated_state

def feedback_node(state: AgentState) -> AgentState:
    """The Brand Guardian provides FEEDBACK on the draft."""
    print("--- [Node: Feedback] ---")
    
    model = get_model_with_fallback()
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
    'score': float (0-1),
    'breakdown': {{
        'tone': float (0-1),
        'visual': float (0-1),
        'structure': float (0-1)
    }}
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

def updates_skill_node(state: AgentState) -> AgentState:
    """The agent UPDATES ITS SKILL by researching and learning from context."""
    print("--- [Node: Updates Skill] ---")
    
    model = get_model_with_fallback()
    bm = BrandManager()
    
    # 1. Research for more facts
    query = state["user_request"]
    new_facts = research_skill(query, depth=state["iteration_count"])
    
    # 2. Extract a 'Brand Lesson' if we have feedback
    new_memory_id = None
    if state["feedback_history"]:
        last_feedback = state["feedback_history"][-1]
        if last_feedback.score < 0.8:  # Only learn if there was significant room for improvement
            learn_prompt = f"""
            Based on this feedback: '{last_feedback.suggestions}', 
            extract a single, concise brand guideline that should be followed in future.
            Example: 'Always avoid using the word synergy when describing AI features.'
            Output only the guideline text.
            """
            lesson = model.invoke([HumanMessage(content=learn_prompt)]).content
            
            # Store the lesson in BrandManager
            import uuid
            lesson_id = f"lesson_{uuid.uuid4().hex[:8]}"
            bm.add_guideline(BrandGuideline(
                id=lesson_id,
                content=lesson,
                category="learned_lesson"
            ))
            print(f"Learned a new skill: {lesson}")

    return {
        **state,
        "research_notes": state["research_notes"] + new_facts
    }
