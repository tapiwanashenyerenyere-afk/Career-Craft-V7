"""
CareerCraft AI - Professional Career Intelligence
Clean, minimalist, high-contrast design.
"""
import streamlit as st
import pandas as pd
import json
import uuid
import time
from datetime import datetime, timedelta
from pathlib import Path

# API Client Imports
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="⚡", # Minimalist icon
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Data & State Init
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "step" not in st.session_state:
    st.session_state.step = "landing"
if "skills" not in st.session_state:
    st.session_state.skills = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "coach_provider" not in st.session_state:
    st.session_state.coach_provider = "gemini" # Default to Gemini if available

DATA_DIR = Path("careercraft_data")
DATA_DIR.mkdir(exist_ok=True)

# =============================================================================
# DATA DEFINITIONS
# =============================================================================

SKILL_GROUPS = {
    "Thinking": {
        "intro": "Strategic & Analytical Skills",
        "skills": [
            {"name": "Problem Solving", "question": "Complexity of problems you solve?"},
            {"name": "Strategic Planning", "question": "Time horizon you plan for?"},
            {"name": "Data Analysis", "question": "Depth of your data usage?"}
        ]
    },
    "Technical": {
        "intro": "Technical & Tooling Proficiency",
        "skills": [
            {"name": "System Architecture", "question": "Scale of systems you build?"},
            {"name": "Coding/Automation", "question": "Frequency of technical work?"},
            {"name": "Tool Mastery", "question": "Speed of learning new tools?"}
        ]
    },
    "People": {
        "intro": "Leadership & Communication",
        "skills": [
            {"name": "Stakeholder Mgmt", "question": "Seniority of people you influence?"},
            {"name": "Team Leadership", "question": "Size of team you lead?"},
            {"name": "Communication", "question": "Clarity of complex ideas?"}
        ]
    },
    "Execution": {
        "intro": "Delivery & Operations",
        "skills": [
            {"name": "Project Mgmt", "question": "Complexity of projects led?"},
            {"name": "Operational Rigor", "question": "Reliability of your output?"},
            {"name": "Speed to Value", "question": "Pace of delivery?"}
        ]
    }
}

CAREERS = [
    {"id": "pm", "title": "Product Manager", "range": "$110k - $220k", "match_skills": ["Problem Solving", "Strategic Planning", "Stakeholder Mgmt"]},
    {"id": "swe", "title": "Software Engineer", "range": "$100k - $250k", "match_skills": ["System Architecture", "Coding/Automation", "Problem Solving"]},
    {"id": "data", "title": "Data Scientist", "range": "$120k - $240k", "match_skills": ["Data Analysis", "Coding/Automation", "Problem Solving"]},
    {"id": "em", "title": "Engineering Manager", "range": "$160k - $300k", "match_skills": ["Team Leadership", "Stakeholder Mgmt", "System Architecture"]},
    {"id": "strat", "title": "Strategy Ops", "range": "$110k - $190k", "match_skills": ["Strategic Planning", "Operational Rigor", "Data Analysis"]},
]

# =============================================================================
# STYLES (Clean, Professional, No Images)
# =============================================================================

st.markdown("""
<style>
    /* Global Reset & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        color: #111827 !important;
        background-color: #FFFFFF !important;
    }
    
    h1, h2, h3 {
        color: #111827 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    
    /* Clean Buttons */
    div.stButton > button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        border: 1px solid #E5E7EB !important;
        background-color: #FFFFFF !important;
        color: #374151 !important;
        transition: all 0.2s !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }
    
    div.stButton > button:hover {
        border-color: #000000 !important;
        color: #000000 !important;
    }
    
    /* Primary Action Buttons */
    div.stButton > button[kind="primary"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #000000 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #333333 !important;
        border-color: #333333 !important;
    }
    
    /* Cards (CSS Only) */
    .clean-card {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 2rem;
        background: #FAFAFA;
        transition: border-color 0.2s;
    }
    .clean-card:hover {
        border-color: #000000;
        background: #FFFFFF;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #111827;
    }
    
    .card-text {
        font-size: 0.95rem;
        color: #6B7280;
        line-height: 1.5;
    }

    /* Progress Indicators */
    .step-indicator {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9CA3AF;
        margin-bottom: 0.5rem;
    }
    
    /* Input Fields */
    .stTextInput input {
        border-radius: 6px !important;
        border: 1px solid #E5E7EB !important;
    }
    .stTextInput input:focus {
        border-color: #000000 !important;
        box-shadow: none !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# =============================================================================
# LOGIC & ALGORITHMS
# =============================================================================

def get_matches():
    # Simple logic regarding skill overlap
    # In a real app this would be properly weighted
    results = []
    user_skills = st.session_state.skills
    
    for c in CAREERS:
        match_score = 0
        reason = []
        for s in c["match_skills"]:
            val = user_skills.get(s, 0)
            if val >= 60: # Threshold
                match_score += 1
            else:
                reason.append(s)
        
        pct = int((match_score / 3) * 100)
        results.append({
            **c, 
            "match": pct, 
            "gaps": reason
        })
    
    return sorted(results, key=lambda x: x['match'], reverse=True)

def generate_coach_response(user_input):
    provider = st.session_state.coach_provider
    context = f"User Skills: {st.session_state.skills}. Top Matches: {[m['title'] for m in get_matches()[:2]]}."
    
    sys_prompt = "You are a senior executive career coach. Be direct, strategic, and concise. No fluff. Focus on high-value actions."

    # 1. Gemini
    if provider == "gemini" and GEMINI_AVAILABLE and st.secrets.get("GEMINI_API_KEY"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(f"{sys_prompt}\nContext:{context}\nUser: {user_input}")
            return response.text
        except:
            return "Gemini API Error. Check keys."

    # 2. OpenAI
    elif provider == "openai" and OPENAI_AVAILABLE and st.secrets.get("OPENAI_API_KEY"):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f"Context: {context}\n\n{user_input}"}
                ]
            )
            return completion.choices[0].message.content
        except:
            return "OpenAI API Error. Check keys."
            
    # 3. Fallback
    else:
        return "AI capabilities are not configured. Please add GEMINI_API_KEY or OPENAI_API_KEY to secrets."

# =============================================================================
# SCREENS
# =============================================================================

def render_landing():
    # Minimalist Hero
    st.markdown("""
    <div style="padding: 4rem 0 3rem 0; text-align: left; max-width: 800px;">
        <h1 style="font-size: 3.5rem; line-height: 1.1; margin-bottom: 1.5rem;">
            Build the life you want.
        </h1>
        <p style="font-size: 1.25rem; color: #4B5563; margin-bottom: 2.5rem; max-width: 600px;">
            Professional career intelligence. Map your skills, identify gaps, and get a strategic sprint plan. No fluff, just leverage.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="clean-card">
            <div class="card-title">Start from Skills</div>
            <div class="card-text">
                Map your current capability stack. We'll tell you what role fits and what you're worth.
            </div>
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Assessment →", type="primary", use_container_width=True):
            st.session_state.step = "skills_1"
            st.rerun()
            
    with col2:
        st.markdown("""
        <div class="clean-card">
            <div class="card-title">Explore Market</div>
            <div class="card-text">
                Browse roles and salary bands. See exactly what skills you are missing for the next level.
            </div>
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Roles", use_container_width=True):
            st.session_state.step = "market"
            st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="display: flex; gap: 2rem; color: #6B7280; font-size: 0.875rem;">
        <span>Powered by Gemini 1.5 & GPT-4</span>
        <span>Deterministic Scoring</span>
        <span>Secure & Private</span>
    </div>
    """, unsafe_allow_html=True)

def render_skills(section_name, next_step):
    group = SKILL_GROUPS[section_name]
    
    st.markdown(f'<div class="step-indicator">ASSESSMENT • {section_name.upper()}</div>', unsafe_allow_html=True)
    st.markdown(f"## {group['intro']}")
    st.markdown("---")
    
    for skill in group["skills"]:
        st.markdown(f"#### {skill['name']}")
        st.markdown(f"<span style='color: #6B7280'>{skill['question']}</span>", unsafe_allow_html=True)
        
        current_val = st.session_state.skills.get(skill["name"], 0)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("Junior / Low", key=f"{skill['name']}_20", use_container_width=True, type="primary" if current_val==20 else "secondary"):
                st.session_state.skills[skill["name"]] = 20
        with c2:
            if st.button("Mid-Level", key=f"{skill['name']}_50", use_container_width=True, type="primary" if current_val==50 else "secondary"):
                st.session_state.skills[skill["name"]] = 50
        with c3:
            if st.button("Senior", key=f"{skill['name']}_80", use_container_width=True, type="primary" if current_val==80 else "secondary"):
                st.session_state.skills[skill["name"]] = 80
        with c4:
            if st.button("Expert / Lead", key=f"{skill['name']}_100", use_container_width=True, type="primary" if current_val==100 else "secondary"):
                st.session_state.skills[skill["name"]] = 100
        
        st.markdown("<div style='margin-bottom: 2rem'></div>", unsafe_allow_html=True)

    c_back, c_next = st.columns([1, 1])
    with c_back:
        if st.button("← Back"):
            st.session_state.step = "landing"
            st.rerun()
    with c_next:
        if st.button("Continue →", type="primary"):
            st.session_state.step = next_step
            st.rerun()

def render_results():
    st.markdown("## Strategic Analysis")
    st.markdown("Based on your capability map, here are your highest leverage opportunities.")
    st.markdown("---")
    
    matches = get_matches()
    
    # Top Result
    best = matches[0]
    st.markdown(f"""
    <div style="border: 2px solid #000; border-radius: 8px; padding: 2rem; margin-bottom: 2rem;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <span style="background: #000; color: #FFF; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; uppercase;">TOP MATCH</span>
                <h2 style="margin-top: 0.5rem; margin-bottom: 0.25rem;">{best['title']}</h2>
                <div style="color: #6B7280; font-family: monospace;">{best['range']}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2rem; font-weight: 700;">{best['match']}%</div>
                <div style="font-size: 0.75rem; color: #6B7280;">ALIGNMENT</div>
            </div>
        </div>
        <br>
        <div style="font-weight: 600; font-size: 0.875rem;">CRITICAL GAPS TO CLOSE:</div>
        <div style="color: #4B5563; margin-top: 0.25rem;">
            {', '.join(best['gaps']) if best['gaps'] else "None. You are ready for this role."}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Other Results
    col1, col2 = st.columns(2)
    for i, res in enumerate(matches[1:3]):
        with col1 if i==0 else col2:
            st.markdown(f"""
            <div class="clean-card">
                <div style="font-weight: 600;">{res['title']}</div>
                <div style="font-size: 0.875rem; color: #6B7280;">{res['match']}% Match</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("## AI Executive Coach")
    st.markdown("Ask strategic questions about your transition. Integrated with live market data models.")
    
    # Chat Interface
    chat_container = st.container()
    
    # Provider Selection
    col_prov, col_space = st.columns([1, 4])
    with col_prov:
        prov = st.selectbox("Model", ["Gemini 1.5", "GPT-4"], index=0 if st.session_state.coach_provider == "gemini" else 1)
        st.session_state.coach_provider = "gemini" if "Gemini" in prov else "openai"

    if prompt := st.chat_input("Ex: 'How do I bridge the gap to Product Manager given my background?'"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = generate_coach_response(prompt)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Upgrade / CTA Section
    st.markdown("---")
    st.markdown("""
    <div style="background: #F3F4F6; padding: 3rem; text-align: center; border-radius: 12px; margin-top: 3rem;">
        <h2>Ready for the deeper work?</h2>
        <p style="color: #4B5563; max-width: 500px; margin: 1rem auto;">
            Create an account to unlock full market datasets, verified salary bands, and a 12-week assisted sprint plan.
        </p>
        <button style="
            background: #000; color: #fff; padding: 1rem 2rem; border: none; border-radius: 6px; 
            font-weight: 600; cursor: pointer; font-size: 1rem;">
            Create Analysis Account
        </button>
        <p style="font-size: 0.75rem; margin-top: 1rem; color: #6B7280;">Get advanced analytics to help you build the life you want.</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# ROUTER
# =============================================================================

def main():
    step = st.session_state.step
    
    if step == "landing":
        render_landing()
    elif step == "skills_1":
        render_skills("Thinking", "skills_2")
    elif step == "skills_2":
        render_skills("Technical", "skills_3")
    elif step == "skills_3":
        render_skills("People", "skills_4")
    elif step == "skills_4":
        render_skills("Execution", "results")
    elif step == "results":
        render_results()
    else:
        st.session_state.step = "landing"
        st.rerun()

if __name__ == "__main__":
    main()
