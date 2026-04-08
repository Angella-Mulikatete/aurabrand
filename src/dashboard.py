import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from src.state import AgentState, BrandContext
from src.graph import create_brand_graph
from src.knowledge.brand_manager import BrandManager

load_dotenv()

# Page Config
st.set_page_config(
    page_title="AuraBrand Command Center",
    page_icon="✨",
    layout="wide"
)

# Custom Styles
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #7d33ff;
        color: white;
    }
    .compliance-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e2130;
        border: 1px solid #3d4156;
    }
</style>
""", unsafe_allow_html=True)

st.title(" AuraBrand Command Center")
st.subheader("The Self-Improving, Brand-Aware Document Suite")

# Sidebar - Brand Configuration
with st.sidebar:
    st.header(" Brand Identity")
    brand_name = st.text_input("Brand Name", "AuraBrand")
    brand_tone = st.selectbox("Tone of Voice", 
                              ["Inspirational", "Professional", "Technical", "Warm", "Bold"])
    brand_guidelines = st.text_area("Style Guidelines", 
                                   "Premium, innovative, and human-centric. Avoid jargon.")
    forbidden = st.text_input("Forbidden Terms (comma separated)", "synergy, paradigm shift")
    
    st.divider()
    st.header(" Brain & Memory")
    bm = BrandManager()
    provider = os.getenv("VECTOR_DB_PROVIDER", "chroma")
    st.info(f"Active Provider: **{provider.upper()}**")
    
    count = bm.get_count()
    st.metric("Learned Brand Insights", count)
    
    if st.button("Clear Memory"):
        bm.clear_brand_data()
        st.success("Memory cleared!")
        st.rerun()

    st.divider()
    st.header(" Model Settings")
    provider = st.selectbox("LLM Provider", ["google", "openai", "anthropic", "groq"])
    max_iters = st.slider("Max Iterations", 1, 5, 3)

# Main Application Logic
if "events" not in st.session_state:
    st.session_state.events = []

col1, col2 = st.columns([2, 1])

with col1:
    user_req = st.text_area("What should I create for you?", 
                            "Write a blog post about the future of AI agents in design.")
    
    if st.button("Generate & Refine"):
        st.session_state.events = []
        
        # Initialize Graph
        app = create_brand_graph()
        
        # Build Initial State
        brand_ctx = BrandContext(
            name=brand_name,
            guidelines=brand_guidelines,
            tone=brand_tone,
            forbidden_terms=[t.strip() for t in forbidden.split(",")]
        )
        
        state: AgentState = {
            "user_request": user_req,
            "brand_context": brand_ctx,
            "current_draft": "",
            "research_notes": [],
            "feedback_history": [],
            "iteration_count": 0,
            "max_iterations": max_iters,
            "final_document": None
        }
        
        # Override Provider in ENV for this run
        os.environ["DEFAULT_LLM_PROVIDER"] = provider
        
        # Run and Stream
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for event in app.stream(state):
            for node, s in event.items():
                st.session_state.events.append({"node": node, "state": s})
                status_text.write(f"**Agent '{node.capitalize()}' is working...**")
                
        progress_bar.progress(100)
        st.success("Refinement Complete!")

# Visualizing Results
if st.session_state.events:
    last_state = st.session_state.events[-1]["state"]
    
    tab1, tab2, tab3 = st.tabs([" Final Document", " Improvement Metrics", " Research Context"])
    
    with tab1:
        st.markdown(f"### Result ({provider.upper()})")
        st.info(last_state.get("current_draft", "No draft generated yet."))
        
    with tab2:
        st.subheader("Performance Over Iterations")
        feedback_list = last_state.get("feedback_history", [])
        if feedback_list:
            scores = [f.score for f in feedback_list]
            df = pd.DataFrame({"Iteration": range(1, len(scores)+1), "Compliance Score": scores})
            fig = px.line(df, x="Iteration", y="Compliance Score", title="Brand Compliance Score",
                          markers=True, line_shape="spline")
            fig.update_layout(yaxis_range=[0, 1])
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("#### Latest Feedback")
            st.json(feedback_list[-1].model_dump())
        else:
            st.write("Waiting for first review...")

    with tab3:
        st.subheader("External Knowledge Gathered")
        for note in last_state.get("research_notes", []):
            st.write(f"- {note}")

with col2:
    st.markdown("""
    <div class="compliance-card">
        <h3> Real-time Audit</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.events:
        for idx, e in enumerate(st.session_state.events):
            with st.expander(f"Step {idx+1}: {e['node']}"):
                st.write(f"**Iteration:** {e['state'].get('iteration_count')}")
                if "feedback_history" in e["state"] and e["state"]["feedback_history"]:
                    st.write(f"Score: {e['state']['feedback_history'][-1].score}")

st.divider()
st.caption("Powered by LangGraph & AuraBrand Architecture | Model Agnostic Engine")
