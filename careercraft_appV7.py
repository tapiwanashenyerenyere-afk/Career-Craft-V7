"""
CareerCraft AI - Human-Centered Career Intelligence
"""
import streamlit as st
import json
import uuid
import base64
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import time

# Optional: Anthropic for AI Coach
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    
# Optional: OpenAI for AI Coach (Fallback)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Data directory
DATA_DIR = Path("careercraft_data")
DATA_DIR.mkdir(exist_ok=True)

# =============================================================================
# DATA DEFINITIONS
# =============================================================================

SKILL_GROUPS = {
    "Thinking": {
        "image": "skill-thinking.jpg",
        "intro": "Let's start with how you think.",
        "skills": [
            {"name": "Problem solving", "question": "How often do you work through complex problems?"},
            {"name": "Learning quickly", "question": "How quickly do you pick up new concepts?"},
            {"name": "Analytical thinking", "question": "How often do you analyze information deeply?"}
        ]
    },
    "Technical": {
        "image": "skill-technical.jpg",
        "intro": "Now let's look at your technical side.",
        "skills": [
            {"name": "Working with data", "question": "How comfortable are you working with data?"},
            {"name": "Digital tools", "question": "How easily do you learn new software and tools?"},
            {"name": "Building systems", "question": "How often do you create processes or systems?"}
        ]
    },
    "People": {
        "image": "skill-people.jpg",
        "intro": "Let's explore how you work with others.",
        "skills": [
            {"name": "Explaining ideas", "question": "How clearly can you explain complex ideas?"},
            {"name": "Supporting others", "question": "How naturally do you help and support teammates?"},
            {"name": "Leading people", "question": "How comfortable are you leading a group?"}
        ]
    },
    "Delivery": {
        "image": "skill-delivery.jpg",
        "intro": "Finally, how you get things done.",
        "skills": [
            {"name": "Finishing tasks", "question": "How reliably do you complete what you start?"},
            {"name": "Managing time", "question": "How well do you manage competing priorities?"},
            {"name": "Handling pressure", "question": "How do you perform under deadline pressure?"}
        ]
    }
}

SKILL_LEVELS = [
    {"label": "Rarely", "value": 20, "description": "Not a regular part of my work"},
    {"label": "Sometimes", "value": 45, "description": "I do this occasionally"},
    {"label": "Often", "value": 70, "description": "A regular part of my week"},
    {"label": "Daily", "value": 95, "description": "I do this almost every day"}
]

CAREERS = [
    {
        "id": "pm",
        "title": "Product Manager",
        "subtitle": "Shape what gets built",
        "range": "$95k–$180k",
        "p50": 140000,
        "skills": ["Problem solving", "Leading people", "Explaining ideas"]
    },
    {
        "id": "dev",
        "title": "Software Developer",
        "subtitle": "Build and create",
        "range": "$80k–$200k",
        "p50": 132000,
        "skills": ["Working with data", "Problem solving", "Building systems"]
    },
    {
        "id": "data",
        "title": "Data Analyst",
        "subtitle": "Find insights in numbers",
        "range": "$65k–$130k",
        "p50": 85000,
        "skills": ["Working with data", "Analytical thinking", "Digital tools"]
    },
    {
        "id": "ux",
        "title": "UX Designer",
        "subtitle": "Design for humans",
        "range": "$70k–$150k",
        "p50": 98000,
        "skills": ["Problem solving", "Explaining ideas", "Digital tools"]
    },
    {
        "id": "marketing",
        "title": "Marketing Manager",
        "subtitle": "Tell compelling stories",
        "range": "$75k–$160k",
        "p50": 110000,
        "skills": ["Explaining ideas", "Digital tools", "Managing time"]
    },
    {
        "id": "consultant",
        "title": "Consultant",
        "subtitle": "Solve business problems",
        "range": "$80k–$170k",
        "p50": 99000,
        "skills": ["Problem solving", "Analytical thinking", "Explaining ideas"]
    }
]

# =============================================================================
# STYLES & ASSETS
# =============================================================================

def load_css():
    st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=DM+Sans:wght@400;500;600&display=swap');

    /* Variables */
    :root {
        --cream: #FBF8F3;
        --cream-dark: #F5F0E8;
        --sage: #4A6741;
        --sage-light: #E8EFE6;
        --sage-dark: #3d5636;
        --terracotta: #C75B39;
        --charcoal: #1F2421;
        --charcoal-light: #374151;
        --grey-medium: #6B7280;
    }

    /* Base styles */
    .stApp {
        background-color: #FBF8F3;
        font-family: 'DM Sans', sans-serif;
        color: #1F2421;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Fraunces', serif !important;
        color: #1F2421 !important;
    }

    p, span, div {
        color: #1F2421;
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Button Overrides */
    div.stButton > button {
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        border: none;
        box-shadow: 0 4px 12px rgba(74, 103, 65, 0.2);
        transition: all 0.2s ease;
    }
    
    /* Primary buttons */
    div.stButton > button[kind="primary"] {
        background-color: #4A6741 !important;
        color: white !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #3d5636 !important;
    }

    /* Secondary buttons */
    div.stButton > button[kind="secondary"] {
        background-color: white !important;
        color: #374151 !important;
        border: 2px solid #E5E7EB !important;
        box-shadow: none !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #4A6741 !important;
        color: #4A6741 !important;
    }
    
    /* Custom Components */
    .hero-container {
        position: relative;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 2rem;
        color: white;
        padding: 4rem 2rem;
        text-align: center;
        background-color: #1F2421; /* Fallback */
    }
    
    .hero-text {
        position: relative;
        z-index: 2;
    }
    
    .hero-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.4);
        z-index: 1;
    }
    
    .entry-card {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .entry-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
    }
    
    .entry-content {
        padding: 1.5rem;
    }
    
    /* Progress */
    .progress-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #E5E7EB;
        transition: all 0.3s ease;
    }

    .dot.active {
        background: #4A6741;
        transform: scale(1.2);
    }

    .dot.done {
        background: #4A6741;
    }
    
    /* Timeline - Dark Card */
    .timeline-card {
        background: #1F2421;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        color: white;
    }

    .timeline {
        position: relative;
        padding-left: 2rem;
        border-left: 3px solid #6B7280; 
        /* Basic border if gradient fails, but we can try fancy */
        border-image: linear-gradient(180deg, #4A6741, #3B82F6, #C75B39) 1;
    }
    
    .timeline::before {
        content: '';
        position: absolute;
        left: 0px; 
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #4A6741, #3B82F6, #C75B39);
        border-radius: 2px;
    }


    .timeline-item {
        position: relative;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
    }
    
    .timeline-title {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        color: white;
        margin-bottom: 0.25rem;
    }
    
    .timeline-body {
        font-size: 0.9rem;
        color: #D1D5DB;
        line-height: 1.5;
    }

    /* Integration Buttons */
    .integration-btn-claude { 
        background-color: #D97706 !important; 
        color: white !important;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }
    .integration-btn-gpt { 
        background-color: #10A37F !important; 
        color: white !important;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }

    /* Animation */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-enter {
        animation: slideUp 0.4s ease-out;
    }
    
    /* Tweaks to ensure text visibility */
    .stMarkdown, .stText {
        color: #1F2421 !important;
    }
    
    /* Fix input fields contrast */
    input, textarea {
        color: #1F2421 !important;
        background-color: white !important;
    }
    
</style>
    """, unsafe_allow_html=True)

def get_image_path(filename):
    img_path = Path("images") / filename
    if img_path.exists():
        return str(img_path)
    return None

def load_image_as_base64(filename):
    path = get_image_path(filename)
    if path:
        try:
            with open(path, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except Exception:
            return None
    return None

# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state():
    # Basic session tracking
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    
    # Navigation state
    if "step" not in st.session_state:
        st.session_state.step = "landing" # landing | skills | career | results
    
    if "entry_mode" not in st.session_state:
        st.session_state.entry_mode = None # skills | career

    # Skills path state
    if "skill_section_idx" not in st.session_state:
        st.session_state.skill_section_idx = 0
    
    if "skill_question_idx" not in st.session_state:
        st.session_state.skill_question_idx = 0
        
    # Data collection
    if "skills" not in st.session_state:
        st.session_state.skills = {}
        
    if "exploring_careers" not in st.session_state:
        st.session_state.exploring_careers = []
        
    # Coach
    if "coach_messages" not in st.session_state:
        st.session_state.coach_messages = []
        
    if "coach_provider" not in st.session_state:
        st.session_state.coach_provider = None

# =============================================================================
# LOGIC
# =============================================================================

def get_skill_score(skill_name):
    return st.session_state.skills.get(skill_name, 0)

def calculate_matches():
    results = []
    user_skills = st.session_state.skills
    
    if not user_skills:
        return []

    for career in CAREERS:
        required = career["skills"]
        matches = 0
        gaps = []
        
        for s in required:
            score = user_skills.get(s, 0)
            if score >= 45: # "Sometimes" or higher
                matches += 1
            else:
                gaps.append(s)
                
        match_pct = int((matches / len(required)) * 100)
        
        results.append({
            **career,
            "match_pct": match_pct,
            "gaps": gaps
        })
    
    results.sort(key=lambda x: x["match_pct"], reverse=True)
    return results

def get_ai_coach_response(user_input, context):
    # 1. Try Claude
    if ANTHROPIC_AVAILABLE and st.secrets.get("ANTHROPIC_API_KEY") and st.secrets.get("LLM_PROVIDER") == "anthropic":
        try:
            client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            system_prompt = "You are a gentle, honest career coach. Help people think through career decisions. Keep responses under 300 words. Be warm but direct."
            
            messages = [{"role": "user", "content": f"Context: {context}\n\nUser Question: {user_input}"}]
            
            resp = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=400,
                system=system_prompt,
                messages=messages
            )
            return resp.content[0].text, "Claude"
        except Exception as e:
            pass 
            
    # 2. Try OpenAI
    if OPENAI_AVAILABLE and st.secrets.get("OPENAI_API_KEY"):
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a gentle, honest career coach."},
                    {"role": "user", "content": f"Context: {context}\n\nUser Question: {user_input}"}
                ]
            )
            return resp.choices[0].message.content, "GPT-4"
        except Exception:
            pass

    # 3. Fallback
    return "That's a great question. Based on your profile, I'd suggest starting small. Pick one skill to improve this week. Look for a small project where you can apply it.", "Fallback"

# =============================================================================
# SCREENS
# =============================================================================

def screen_landing():
    hero_img = load_image_as_base64("hero-crossroads.jpg")
    bg_style = f"background-image: url('data:image/jpg;base64,{hero_img}'); background-size: cover; background-position: center;" if hero_img else "background-color: #1F2421;"
    
    st.markdown(f"""
    <div class="hero-container" style="{bg_style}">
        <div class="hero-overlay"></div>
        <div class="hero-text">
            <h1>Find your path forward</h1>
            <p style="font-size: 1.2rem; margin-top: 1rem; color: #FBF8F3;">Discover careers that fit your natural strengths.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### How would you like to start?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        card_img = load_image_as_base64("card-skills.jpg")
        img_src = f"data:image/jpg;base64,{card_img}" if card_img else "https://placehold.co/600x400/F5F0E8/1F2421?text=Skills"
        
        st.markdown(f"""
        <div class="entry-card">
            <div style="height: 200px; overflow: hidden;">
                <img src="{img_src}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div class="entry-content">
                <h3>Start from my skills</h3>
                <p>Map what you're good at. We'll suggest directions that fit.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start with Skills →", key="btn_start_skills", type="primary", use_container_width=True):
            st.session_state.entry_mode = "skills"
            st.session_state.step = "skills"
            st.rerun()

    with col2:
        card_img = load_image_as_base64("card-career.jpg")
        img_src = f"data:image/jpg;base64,{card_img}" if card_img else "https://placehold.co/600x400/F5F0E8/1F2421?text=Careers"
        
        st.markdown(f"""
        <div class="entry-card">
            <div style="height: 200px; overflow: hidden;">
                <img src="{img_src}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div class="entry-content">
                <h3>Start from a career</h3>
                <p>Curious about a specific role? See your gaps.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Browse Careers →", key="btn_start_careers", type="secondary", use_container_width=True):
            st.session_state.entry_mode = "career"
            st.session_state.step = "career"
            st.rerun()

def screen_skills_path():
    groups = list(SKILL_GROUPS.keys()) 
    current_group_name = groups[st.session_state.skill_section_idx]
    current_group = SKILL_GROUPS[current_group_name]
    
    skills_in_group = current_group["skills"]
    current_skill = skills_in_group[st.session_state.skill_question_idx]
    
    # Progress
    dots_html = ""
    for i, g in enumerate(groups):
        cls = "dot"
        if i < st.session_state.skill_section_idx:
            cls += " done"
        elif i == st.session_state.skill_section_idx:
            cls += " active"
        dots_html += f'<span class="{cls}"></span>'
        
    st.markdown(f"""
    <div class="progress-container">
        <div style="display: flex; gap: 0.5rem;">{dots_html}</div>
        <div style="font-size: 0.85rem; color: #6B7280; font-weight: 500;">{current_group_name}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        img_b64 = load_image_as_base64(current_group["image"])
        if img_b64:
             st.markdown(f"""
             <div style="border-radius: 16px; overflow: hidden; margin-bottom: 2rem;">
                <img src="data:image/jpg;base64,{img_b64}" style="width: 100%; object-fit: cover;">
             </div>
             """, unsafe_allow_html=True)
        else:
             st.markdown(f"""
             <div style="background: #E5E5E5; height: 300px; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin-bottom: 2rem;">
                <p style="color: #666;">{current_group_name} Image</p>
             </div>
             """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="animate-enter">
            <p style="color: #6B7280; margin-bottom: 0.5rem;">{current_group['intro']}</p>
            <h2 style="font-size: 2rem; margin-bottom: 2rem; line-height: 1.2;">{current_skill['question']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        current_val = get_skill_score(current_skill['name'])
        
        c1, c2 = st.columns(2)
        with c1:
            lvl = 20
            lbl = f"✓ Rarely" if current_val == lvl else "Rarely"
            typ = "primary" if current_val == lvl else "secondary"
            if st.button(lbl, key=f"btn_rare_{current_skill['name']}", use_container_width=True, type=typ):
                update_skill(current_skill['name'], lvl)

            lvl = 70
            lbl = f"✓ Often" if current_val == lvl else "Often"
            typ = "primary" if current_val == lvl else "secondary"
            if st.button(lbl, key=f"btn_often_{current_skill['name']}", use_container_width=True, type=typ):
                update_skill(current_skill['name'], lvl)

        with c2:
            lvl = 45
            lbl = f"✓ Sometimes" if current_val == lvl else "Sometimes"
            typ = "primary" if current_val == lvl else "secondary"
            if st.button(lbl, key=f"btn_some_{current_skill['name']}", use_container_width=True, type=typ):
                update_skill(current_skill['name'], lvl)

            lvl = 95
            lbl = f"✓ Daily" if current_val == lvl else "Daily"
            typ = "primary" if current_val == lvl else "secondary"
            if st.button(lbl, key=f"btn_daily_{current_skill['name']}", use_container_width=True, type=typ):
                update_skill(current_skill['name'], lvl)

    st.markdown("---")
    if st.button("← Back"):
        go_back()

def update_skill(skill_name, value):
    st.session_state.skills[skill_name] = value
    next_question()

def next_question():
    groups = list(SKILL_GROUPS.keys())
    current_group_name = groups[st.session_state.skill_section_idx]
    skills_in_group = SKILL_GROUPS[current_group_name]["skills"]
    
    if st.session_state.skill_question_idx < len(skills_in_group) - 1:
        st.session_state.skill_question_idx += 1
    else:
        if st.session_state.skill_section_idx < len(groups) - 1:
            st.session_state.skill_section_idx += 1
            st.session_state.skill_question_idx = 0
        else:
            st.session_state.step = "results"
    st.rerun()

def go_back():
    if st.session_state.skill_question_idx > 0:
        st.session_state.skill_question_idx -= 1
    elif st.session_state.skill_section_idx > 0:
        st.session_state.skill_section_idx -= 1
        prev_group = list(SKILL_GROUPS.keys())[st.session_state.skill_section_idx]
        st.session_state.skill_question_idx = len(SKILL_GROUPS[prev_group]["skills"]) - 1
    else:
        st.session_state.step = "landing"
    st.rerun()

def screen_career_selection():
    st.markdown("## Explore Careers")
    if st.button("← Back"):
        st.session_state.step = "landing"
        st.rerun()
        
    for career in CAREERS:
        col1, col2 = st.columns([1, 4])
        with col2:
            st.markdown(f"**{career['title']}**")
            st.markdown(f"{career['subtitle']} • {career['range']}")
        with col1:
             if st.button("Select", key=f"sel_{career['id']}"):
                st.session_state.exploring_careers = [career] 
                st.session_state.step = "results"
                st.rerun()

def screen_results():
    st.markdown("## Your Career Directions")
    
    matches = calculate_matches()
    
    if matches:
        best = matches[0]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F0FDF4, #FFFFFF); border-left: 4px solid #4A6741; padding: 1.5rem; border-radius: 16px; margin-bottom: 2rem;">
            <div style="display:flex; justify-content:space-between;">
                <h3>{best['title']}</h3>
                <span style="background: #DCFCE7; color: #166534; padding: 0.25rem 0.75rem; border-radius: 999px; font-weight: 600; font-size: 0.85rem;">{best['match_pct']}% Match</span>
            </div>
            <p>{best['subtitle']} • {best['range']}</p>
            <div style="background: #E5E7EB; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 1rem;">
                <div style="width: {best['match_pct']}%; background: #4A6741; height: 100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if best["gaps"]:
            st.markdown("### Focus Areas")
            for gap in best["gaps"]:
                st.markdown(f"- **{gap}**: Something to work on")
    
    # Timeline
    st.markdown("""
    <div class="timeline-card">
        <h3 style="color:white; margin-bottom: 1.5rem;">Your Path Forward</h3>
        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-title" style="color:#86EFAC;">DIRECTION (6-12 Months)</div>
                <div class="timeline-body">Explore and move toward Product Manager while building new skills.</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-title" style="color:#93C5FD;">THIS PHASE (3 Months)</div>
                <div class="timeline-body">Exploration & Foundations: Understand the work and build basic skills.</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-title" style="color:#FCA5A5;">NEXT SPRINT (4 Weeks)</div>
                <div class="timeline-body">Talk to 2 PMs, start 1 mini project.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Coach using Integrations
    st.markdown("---")
    st.markdown("### 💬 Deep Dive with AI")
    
    st.markdown("""
    <div style="background: #F9FAFB; padding: 2rem; border-radius: 16px; text-align: center;">
        <p style="margin-bottom: 1rem;">Take your results to Claude or ChatGPT for a full coaching plan.</p>
        <div style="display: flex; gap: 1rem; justify-content: center;">
            <a href="https://claude.ai/new?q=I%20am%20exploring%20Product%20Management.%20My%20strengths%20are%20Problem%20Solving%20and%20Leading%20People.%20Create%20a%20learning%20plan." target="_blank" class="integration-btn-claude">Ask Claude</a>
            <a href="https://chat.openai.com/" target="_blank" class="integration-btn-gpt">Ask ChatGPT</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat
    st.markdown("### OR ask our Coach right here")
    for msg in st.session_state.coach_messages:
        role_style = "background: #F0FDF4; border: 1px solid #BBF7D0;" if msg["role"] == "assistant" else "background: #F3F4F6;"
        st.markdown(f"""
        <div style="{role_style} padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem;">
            {msg['content']}
        </div>
        """, unsafe_allow_html=True)
        
    user_input = st.text_input("Ask about your career path...", key="coach_input")
    if st.button("Ask Coach", type="primary"):
        if user_input:
            st.session_state.coach_messages.append({"role": "user", "content": user_input})
            top_match = matches[0] if matches else None
            context = f"User has matched {top_match['title']}." if top_match else "User is exploring."
            response, provider = get_ai_coach_response(user_input, context)
            
            st.session_state.coach_provider = provider
            st.session_state.coach_messages.append({"role": "assistant", "content": response})
            st.rerun()

    if st.button("← Start Over", type="secondary"):
        st.session_state.clear()
        st.rerun()

def main():
    load_css()
    init_session_state()
    
    if st.session_state.step == "landing":
        screen_landing()
    elif st.session_state.step == "skills":
        screen_skills_path()
    elif st.session_state.step == "career":
        screen_career_selection()
    elif st.session_state.step == "results":
        screen_results()

if __name__ == "__main__":
    main()
