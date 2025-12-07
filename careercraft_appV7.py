"""
CareerCraft – Career Intelligence Platform
7 strategic questions, built-in AI coaches, account creation
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# Optional LLM imports
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

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

# Page config
st.set_page_config(
    page_title="CareerCraft",
    page_icon="C",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# DATA - 7 strategic questions
# =============================================================================

QUESTIONS = [
    {
        "id": "technical",
        "question": "How comfortable are you with data, spreadsheets, and technical tools?",
        "dimension": "Technical aptitude",
        "low_label": "I prefer to avoid them",
        "high_label": "I work with them daily",
    },
    {
        "id": "people_energy",
        "question": "How energized are you after a day of meetings and collaboration versus deep solo work?",
        "dimension": "Social energy",
        "low_label": "Solo work energizes me",
        "high_label": "Collaboration energizes me",
    },
    {
        "id": "people_style",
        "question": "When working with others, do you prefer supporting the team or taking the lead?",
        "dimension": "Interaction style",
        "low_label": "I prefer supporting",
        "high_label": "I naturally lead",
    },
    {
        "id": "analysis",
        "question": "When making decisions, do you rely more on data or intuition?",
        "dimension": "Decision-making",
        "low_label": "Intuition and experience",
        "high_label": "Data and analysis",
    },
    {
        "id": "structure",
        "question": "Do you prefer clear processes and plans or figuring things out as you go?",
        "dimension": "Work structure",
        "low_label": "Flexible and adaptive",
        "high_label": "Structured and planned",
    },
    {
        "id": "learning",
        "question": "How quickly do you typically pick up new skills and domains?",
        "dimension": "Learning velocity",
        "low_label": "I take my time to master",
        "high_label": "I learn very quickly",
    },
    {
        "id": "client_facing",
        "question": "How much do you enjoy working directly with clients or external stakeholders?",
        "dimension": "External orientation",
        "low_label": "Prefer internal work",
        "high_label": "Love client interaction",
    },
]

ANSWER_OPTIONS = [
    {"label": "1", "value": 20},
    {"label": "2", "value": 40},
    {"label": "3", "value": 60},
    {"label": "4", "value": 80},
    {"label": "5", "value": 95},
]

CAREERS = [
    {"id": "pm", "title": "Product Manager", "subtitle": "Shape what gets built", "range": "$95k-$180k",
     "fit": {"technical": 60, "people_energy": 80, "people_style": 75, "analysis": 70, "structure": 60, "learning": 80, "client_facing": 70}},
    {"id": "dev", "title": "Software Developer", "subtitle": "Build and create", "range": "$80k-$200k",
     "fit": {"technical": 95, "people_energy": 40, "people_style": 45, "analysis": 80, "structure": 70, "learning": 90, "client_facing": 30}},
    {"id": "data", "title": "Data Analyst", "subtitle": "Find insights in numbers", "range": "$65k-$130k",
     "fit": {"technical": 85, "people_energy": 45, "people_style": 40, "analysis": 95, "structure": 80, "learning": 70, "client_facing": 50}},
    {"id": "ux", "title": "UX Designer", "subtitle": "Design for humans", "range": "$70k-$150k",
     "fit": {"technical": 50, "people_energy": 70, "people_style": 55, "analysis": 60, "structure": 50, "learning": 80, "client_facing": 75}},
    {"id": "marketing", "title": "Marketing Manager", "subtitle": "Tell compelling stories", "range": "$75k-$160k",
     "fit": {"technical": 40, "people_energy": 85, "people_style": 70, "analysis": 50, "structure": 50, "learning": 70, "client_facing": 85}},
    {"id": "consultant", "title": "Consultant", "subtitle": "Solve business problems", "range": "$80k-$170k",
     "fit": {"technical": 60, "people_energy": 80, "people_style": 75, "analysis": 75, "structure": 70, "learning": 90, "client_facing": 95}},
    {"id": "analyst", "title": "Business Analyst", "subtitle": "Bridge tech and business", "range": "$70k-$130k",
     "fit": {"technical": 70, "people_energy": 65, "people_style": 50, "analysis": 85, "structure": 75, "learning": 75, "client_facing": 60}},
    {"id": "manager", "title": "People Manager", "subtitle": "Lead and develop teams", "range": "$90k-$170k",
     "fit": {"technical": 45, "people_energy": 90, "people_style": 95, "analysis": 55, "structure": 70, "learning": 65, "client_facing": 60}},
]

# =============================================================================
# CUSTOM CSS - Warm, analytical, high contrast, NO emojis
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=DM+Sans:wght@400;500;600&display=swap');
    
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    
    .stApp {
        background: #FAF9F6;
        font-family: 'DM Sans', -apple-system, sans-serif;
    }
    
    .main .block-container {
        padding: 1.5rem 1rem 4rem;
        max-width: 620px;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Fraunces', Georgia, serif !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    p, span, div, label {
        color: #2d2d2d;
    }
    
    /* Top bar */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #e8e5e0;
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .logo-mark {
        width: 32px;
        height: 32px;
        background: #4A6741;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .logo-text {
        font-family: 'Fraunces', serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    .signup-link {
        font-size: 0.85rem;
        color: #4A6741;
        font-weight: 600;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border: 1.5px solid #4A6741;
        border-radius: 6px;
        transition: all 0.2s;
        cursor: pointer;
        background: transparent;
    }
    
    .signup-link:hover {
        background: #4A6741;
        color: white;
    }
    
    /* Progress */
    .progress-container {
        margin-bottom: 2rem;
    }
    
    .progress-text {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 0.4rem;
        font-weight: 500;
    }
    
    .progress-bar {
        height: 4px;
        background: #e8e5e0;
        border-radius: 2px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: #4A6741;
        border-radius: 2px;
        transition: width 0.3s ease;
    }
    
    /* Question */
    .question-container {
        animation: fadeUp 0.3s ease-out;
    }
    
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .question-text {
        font-family: 'Fraunces', Georgia, serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        line-height: 1.4;
        margin-bottom: 1.75rem;
    }
    
    /* Scale */
    .scale-labels {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.75rem;
        font-size: 0.8rem;
        color: #666;
    }
    
    .scale-buttons {
        display: flex;
        gap: 0.4rem;
    }
    
    /* Hero */
    .hero {
        text-align: center;
        padding: 2rem 0;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: white;
        border: 1px solid #e8e5e0;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 1.25rem;
    }
    
    .hero-dot {
        width: 6px;
        height: 6px;
        background: #4A6741;
        border-radius: 50%;
    }
    
    .hero-title {
        font-family: 'Fraunces', Georgia, serif;
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a1a;
        line-height: 1.25;
        margin-bottom: 0.9rem;
    }
    
    .hero-title em {
        font-style: italic;
        color: #4A6741;
    }
    
    .hero-sub {
        font-size: 1rem;
        color: #555;
        line-height: 1.55;
        max-width: 460px;
        margin: 0 auto 1.75rem;
    }
    
    /* Steps */
    .steps {
        display: flex;
        justify-content: center;
        gap: 1.25rem;
        margin: 1.75rem 0;
    }
    
    .step {
        text-align: center;
        max-width: 130px;
    }
    
    .step-num {
        width: 36px;
        height: 36px;
        background: #4A6741;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 0.95rem;
        margin: 0 auto 0.5rem;
    }
    
    .step-title {
        font-weight: 600;
        color: #1a1a1a;
        font-size: 0.85rem;
        margin-bottom: 0.15rem;
    }
    
    .step-desc {
        font-size: 0.75rem;
        color: #666;
        line-height: 1.3;
    }
    
    /* Result cards */
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.9rem;
        border: 1px solid #e8e5e0;
    }
    
    .result-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #666;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .pill {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }
    
    .pill-green { background: #e8f5e3; color: #2d5a27; }
    .pill-amber { background: #fef3e2; color: #8a5a00; }
    
    /* Direction cards */
    .direction-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.6rem;
        border-left: 3px solid;
        position: relative;
    }
    
    .direction-primary {
        border-color: #4A6741;
        background: linear-gradient(135deg, #f5faf4 0%, white 100%);
    }
    
    .direction-secondary {
        border-color: #2563eb;
        background: linear-gradient(135deg, #f0f7ff 0%, white 100%);
    }
    
    .direction-tertiary {
        border-color: #d97706;
        background: linear-gradient(135deg, #fffbf0 0%, white 100%);
    }
    
    .direction-type {
        font-size: 0.6rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    
    .direction-primary .direction-type { color: #2d5a27; }
    .direction-secondary .direction-type { color: #1d4ed8; }
    .direction-tertiary .direction-type { color: #b45309; }
    
    .direction-title {
        font-family: 'Fraunces', serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.2rem;
    }
    
    .direction-meta {
        font-size: 0.8rem;
        color: #555;
    }
    
    .direction-match {
        position: absolute;
        top: 0.8rem;
        right: 0.8rem;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 999px;
    }
    
    .direction-primary .direction-match { background: #e8f5e3; color: #2d5a27; }
    .direction-secondary .direction-match, .direction-tertiary .direction-match { background: #fef3e2; color: #8a5a00; }
    
    /* Timeline */
    .timeline-card {
        background: #1a1a1a;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
    }
    
    .timeline-header {
        font-size: 0.6rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #999;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .timeline {
        position: relative;
        padding-left: 1.4rem;
    }
    
    .timeline::before {
        content: '';
        position: absolute;
        left: 4px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(180deg, #4A6741, #2563eb, #d97706);
        border-radius: 1px;
    }
    
    .tl-item {
        position: relative;
        margin-bottom: 0.9rem;
        padding: 0.65rem;
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
    }
    
    .tl-item::before {
        content: '';
        position: absolute;
        left: -1.15rem;
        top: 0.75rem;
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    
    .tl-week1::before { background: #4A6741; }
    .tl-week2::before { background: #2563eb; }
    .tl-week3::before { background: #d97706; }
    
    .tl-label {
        font-size: 0.55rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        font-weight: 600;
        margin-bottom: 0.15rem;
    }
    
    .tl-week1 .tl-label { color: #86efac; }
    .tl-week2 .tl-label { color: #93c5fd; }
    .tl-week3 .tl-label { color: #fcd34d; }
    
    .tl-title {
        font-family: 'Fraunces', serif;
        font-size: 0.9rem;
        color: #f5f5f5;
        line-height: 1.35;
    }
    
    /* Coach section */
    .coach-section {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        border: 1px solid #e8e5e0;
    }
    
    .coach-title {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.35rem;
    }
    
    .coach-subtitle {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 1rem;
    }
    
    .coach-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e8e5e0;
        padding-bottom: 0.75rem;
    }
    
    .coach-tab {
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
        background: #f5f5f5;
        color: #555;
    }
    
    .coach-tab:hover {
        background: #e8e5e0;
    }
    
    .coach-tab.active {
        background: #4A6741;
        color: white;
    }
    
    .coach-tab-claude.active { background: #d97706; }
    .coach-tab-gemini.active { background: #2563eb; }
    .coach-tab-chatgpt.active { background: #10a37f; }
    
    .coach-response {
        background: #f8f8f6;
        border: 1px solid #e8e5e0;
        border-radius: 10px;
        padding: 1.1rem;
        margin-top: 0.9rem;
        font-size: 0.9rem;
        line-height: 1.65;
        color: #2d2d2d;
    }
    
    .coach-provider {
        font-size: 0.7rem;
        color: #888;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Account section */
    .account-section {
        background: linear-gradient(135deg, #f5faf4 0%, #f0f7ff 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.25rem 0;
        text-align: center;
        border: 1px solid #e8e5e0;
    }
    
    .account-title {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.4rem;
    }
    
    .account-subtitle {
        font-size: 0.85rem;
        color: #555;
        margin-bottom: 1rem;
    }
    
    .account-benefits {
        text-align: left;
        margin: 1rem 0;
        padding: 0 1rem;
    }
    
    .account-benefit {
        font-size: 0.85rem;
        color: #2d2d2d;
        margin-bottom: 0.5rem;
        padding-left: 1.25rem;
        position: relative;
    }
    
    .account-benefit::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0.4rem;
        width: 6px;
        height: 6px;
        background: #4A6741;
        border-radius: 50%;
    }
    
    /* Streamlit overrides */
    .stButton > button {
        background: #4A6741 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.7rem 1.4rem !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
        box-shadow: 0 2px 8px rgba(74, 103, 65, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #3d5636 !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #2d2d2d !important;
        border: 1.5px solid #d1d1d1 !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: #4A6741 !important;
        color: #4A6741 !important;
        background: #f5faf4 !important;
    }
    
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 1.5px solid #d1d1d1 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 0.85rem !important;
        background: white !important;
        color: #2d2d2d !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #4A6741 !important;
        box-shadow: 0 0 0 1px #4A6741 !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #999 !important;
    }
    
    .stTextInput input {
        border-radius: 8px !important;
        border: 1.5px solid #d1d1d1 !important;
        padding: 0.7rem !important;
        background: white !important;
        color: #2d2d2d !important;
    }
    
    .footer-note {
        text-align: center;
        font-size: 0.75rem;
        color: #888;
        margin-top: 1.25rem;
        font-style: italic;
    }
    
    /* Radio buttons for coach selection */
    .stRadio > div {
        flex-direction: row !important;
        gap: 0.5rem !important;
    }
    
    .stRadio label {
        background: #f5f5f5 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        border: 1px solid #e8e5e0 !important;
        cursor: pointer !important;
    }
    
    .stRadio label:hover {
        background: #e8e5e0 !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HELPERS
# =============================================================================

def get_secret(key, default=None):
    try:
        return dict(st.secrets).get(key, default)
    except:
        return default

def save_session(data):
    try:
        Path("careercraft_data").mkdir(exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        sid = st.session_state.get("session_id", "unknown")[:8]
        with open(f"careercraft_data/session_{ts}_{sid}.json", "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def calculate_career_matches(answers):
    matches = []
    for career in CAREERS:
        total_diff = 0
        for q in QUESTIONS:
            user_val = answers.get(q["id"], 50)
            career_val = career["fit"].get(q["id"], 50)
            total_diff += abs(user_val - career_val)
        
        max_diff = len(QUESTIONS) * 80
        match_pct = max(0, 100 - int((total_diff / max_diff) * 100))
        matches.append({"career": career, "match": match_pct})
    
    return sorted(matches, key=lambda x: x["match"], reverse=True)

def get_strengths_and_gaps(answers):
    if not answers:
        return ["Problem solving", "Communication"], ["Technical skills"]
    
    dimension_names = {
        "technical": "Technical skills",
        "people_energy": "Collaboration",
        "people_style": "Leadership",
        "analysis": "Analytical thinking",
        "structure": "Organization",
        "learning": "Learning agility",
        "client_facing": "Client relations",
    }
    
    sorted_answers = sorted(answers.items(), key=lambda x: x[1], reverse=True)
    strengths = [dimension_names.get(k, k) for k, v in sorted_answers[:2] if v >= 60]
    gaps = [dimension_names.get(k, k) for k, v in sorted_answers if v <= 40][:2]
    
    if not strengths:
        strengths = [dimension_names.get(sorted_answers[0][0], "Problem solving")]
    if not gaps:
        gaps = [dimension_names.get(sorted_answers[-1][0], "Growth area")]
    
    return strengths, gaps

def generate_context_prompt(strengths, gaps, direction):
    return f"""User's career assessment results:
- Top strengths: {', '.join(strengths)}
- Growth areas: {', '.join(gaps)}
- Direction exploring: {direction}
- 4-week sprint: Talk to 2 {direction}s, start 1 project, sample 1 course"""

# =============================================================================
# AI COACHES
# =============================================================================

COACH_SYSTEM = """You are a thoughtful career coach. Help people think through career decisions with:
1. What matters most right now
2. How to frame the next 3-6 months
3. 1-3 concrete, low-risk experiments

Keep responses under 200 words. Be warm but direct. Speak like a wise colleague, not a corporate coach."""

def get_claude_response(user_msg, context):
    api_key = get_secret("ANTHROPIC_API_KEY")
    if not api_key or not ANTHROPIC_AVAILABLE:
        return None, "API key not configured"
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=350,
            system=COACH_SYSTEM,
            messages=[{"role": "user", "content": f"{context}\n\nUser question: {user_msg}"}]
        )
        return resp.content[0].text.strip(), None
    except Exception as e:
        return None, str(e)

def get_chatgpt_response(user_msg, context):
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key or not OPENAI_AVAILABLE:
        return None, "API key not configured"
    
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=350,
            messages=[
                {"role": "system", "content": COACH_SYSTEM},
                {"role": "user", "content": f"{context}\n\nUser question: {user_msg}"}
            ]
        )
        return resp.choices[0].message.content.strip(), None
    except Exception as e:
        return None, str(e)

def get_gemini_response(user_msg, context):
    api_key = get_secret("GOOGLE_API_KEY")
    if not api_key or not GEMINI_AVAILABLE:
        return None, "API key not configured"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"{COACH_SYSTEM}\n\n{context}\n\nUser question: {user_msg}"
        resp = model.generate_content(prompt)
        return resp.text.strip(), None
    except Exception as e:
        return None, str(e)

# =============================================================================
# SESSION STATE
# =============================================================================

if "step" not in st.session_state:
    st.session_state.step = "landing"
    st.session_state.question_idx = 0
    st.session_state.answers = {}
    st.session_state.coach_response = None
    st.session_state.coach_provider = None
    st.session_state.selected_coach = "claude"
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    st.session_state.show_signup = False

for key in ["coach_provider", "coach_response", "selected_coach"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "selected_coach" else "claude"

# =============================================================================
# COMPONENTS
# =============================================================================

def render_top_bar():
    st.markdown("""
    <div class="top-bar">
        <div class="logo">
            <div class="logo-mark">C</div>
            <div class="logo-text">CareerCraft</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Signup button in top right using columns
    col1, col2, col3 = st.columns([4, 1, 1])
    with col3:
        if st.button("Sign up", key="top_signup", type="secondary"):
            st.session_state.show_signup = True
            st.rerun()

def render_signup_modal():
    st.markdown("""
    <div class="account-section">
        <div class="account-title">Create your account</div>
        <div class="account-subtitle">Save your results and track your progress</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("signup_form"):
        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input("Create password", type="password", placeholder="Min 8 characters")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Create account", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True, type="secondary"):
                st.session_state.show_signup = False
                st.rerun()
        
        if submitted and email and password:
            st.success("Account created! (Demo mode - not actually saved)")
            st.session_state.show_signup = False

# =============================================================================
# LANDING PAGE
# =============================================================================

def render_landing():
    render_top_bar()
    
    if st.session_state.show_signup:
        render_signup_modal()
        return
    
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">
            <span class="hero-dot"></span>
            Free career tool, 3 minutes
        </div>
        <h1 class="hero-title">Get <em>clarity</em> on your career.</h1>
        <p class="hero-sub">
            Answer 7 questions. Get matched to careers with real salary data.
            Talk to AI coaches. Walk away with a 4-week action plan.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="steps">
        <div class="step">
            <div class="step-num">1</div>
            <div class="step-title">7 questions</div>
            <div class="step-desc">About how you work</div>
        </div>
        <div class="step">
            <div class="step-num">2</div>
            <div class="step-title">See matches</div>
            <div class="step-desc">Careers that fit</div>
        </div>
        <div class="step">
            <div class="step-num">3</div>
            <div class="step-title">AI coaches</div>
            <div class="step-desc">Get personalized advice</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start CareerCheck", use_container_width=True):
            st.session_state.step = "questions"
            st.session_state.question_idx = 0
            st.session_state.answers = {}
            st.rerun()
    
    st.markdown('<p class="footer-note">No signup required to start. Create an account to save your results.</p>', unsafe_allow_html=True)

# =============================================================================
# QUESTIONS
# =============================================================================

def render_questions():
    render_top_bar()
    
    if st.session_state.show_signup:
        render_signup_modal()
        return
    
    idx = st.session_state.question_idx
    total = len(QUESTIONS)
    question = QUESTIONS[idx]
    
    progress_pct = int(((idx + 1) / total) * 100)
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-text">Question {idx + 1} of {total}</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_pct}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="question-container">
        <h2 class="question-text">{question['question']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="scale-labels">
        <span>{question['low_label']}</span>
        <span>{question['high_label']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    current_value = st.session_state.answers.get(question["id"], None)
    
    cols = st.columns(5)
    for i, option in enumerate(ANSWER_OPTIONS):
        with cols[i]:
            is_selected = current_value == option["value"]
            btn_type = "primary" if is_selected else "secondary"
            btn_label = option["label"]
            
            if st.button(btn_label, key=f"q_{question['id']}_{option['value']}", 
                        type=btn_type, use_container_width=True):
                st.session_state.answers[question["id"]] = option["value"]
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if idx > 0:
            if st.button("Back", type="secondary", use_container_width=True):
                st.session_state.question_idx -= 1
                st.rerun()
        else:
            if st.button("Exit", type="secondary", use_container_width=True):
                st.session_state.step = "landing"
                st.rerun()
    
    with col3:
        can_continue = current_value is not None
        is_last = idx == total - 1
        
        if is_last:
            if st.button("See results", disabled=not can_continue, use_container_width=True):
                st.session_state.step = "results"
                st.rerun()
        else:
            if st.button("Next", disabled=not can_continue, use_container_width=True):
                st.session_state.question_idx += 1
                st.rerun()

# =============================================================================
# RESULTS
# =============================================================================

def render_results():
    render_top_bar()
    
    if st.session_state.show_signup:
        render_signup_modal()
        return
    
    answers = st.session_state.answers
    matches = calculate_career_matches(answers)
    strengths, gaps = get_strengths_and_gaps(answers)
    
    top_match = matches[0] if matches else {"career": CAREERS[0], "match": 75}
    second_match = matches[1] if len(matches) > 1 else {"career": CAREERS[1], "match": 65}
    third_match = matches[2] if len(matches) > 2 else {"career": CAREERS[2], "match": 55}
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.25rem;">
        <h1 style="font-family: 'Fraunces', serif; font-size: 1.5rem; color: #1a1a1a;">Your Results</h1>
        <p style="color: #666; font-size: 0.9rem;">Based on your 7 answers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Strengths & Gaps
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-label">Your Strengths</div>', unsafe_allow_html=True)
        pills = "".join([f'<span class="pill pill-green">{s}</span>' for s in strengths])
        st.markdown(pills, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-label">Growth Areas</div>', unsafe_allow_html=True)
        pills = "".join([f'<span class="pill pill-amber">{s}</span>' for s in gaps])
        st.markdown(pills, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Career matches
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-label">Career Matches</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="direction-card direction-primary">
        <div class="direction-type">Best match</div>
        <div class="direction-title">{top_match['career']['title']}</div>
        <div class="direction-meta">{top_match['career']['range']} | {top_match['career']['subtitle']}</div>
        <div class="direction-match">{top_match['match']}%</div>
    </div>
    <div class="direction-card direction-secondary">
        <div class="direction-type">Strong fit</div>
        <div class="direction-title">{second_match['career']['title']}</div>
        <div class="direction-meta">{second_match['career']['range']} | {second_match['career']['subtitle']}</div>
        <div class="direction-match">{second_match['match']}%</div>
    </div>
    <div class="direction-card direction-tertiary">
        <div class="direction-type">Consider</div>
        <div class="direction-title">{third_match['career']['title']}</div>
        <div class="direction-meta">{third_match['career']['range']} | {third_match['career']['subtitle']}</div>
        <div class="direction-match">{third_match['match']}%</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Timeline
    top_career = top_match['career']['title']
    st.markdown(f"""
    <div class="timeline-card">
        <div class="timeline-header">Your 4-Week Sprint</div>
        <div class="timeline">
            <div class="tl-item tl-week1">
                <div class="tl-label">Week 1-2</div>
                <div class="tl-title">Talk to 2 {top_career}s about their work</div>
            </div>
            <div class="tl-item tl-week2">
                <div class="tl-label">Week 3</div>
                <div class="tl-title">Start 1 small project to test your interest</div>
            </div>
            <div class="tl-item tl-week3">
                <div class="tl-label">Week 4</div>
                <div class="tl-title">Reflect and decide on next steps</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Coaches section
    st.markdown('<div class="coach-section">', unsafe_allow_html=True)
    st.markdown('<div class="coach-title">Talk to a Career Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="coach-subtitle">Get personalized advice from AI coaches</div>', unsafe_allow_html=True)
    
    # Coach selection
    coach_choice = st.radio(
        "Select coach:",
        ["Claude", "ChatGPT", "Gemini"],
        horizontal=True,
        key="coach_selector",
        label_visibility="collapsed"
    )
    
    user_input = st.text_area(
        "Your question:",
        placeholder="What feels unclear about this career direction? What should I focus on first?",
        key="coach_input",
        label_visibility="collapsed"
    )
    
    if st.button("Get advice", type="primary"):
        if user_input.strip():
            context = generate_context_prompt(strengths, gaps, top_career)
            
            with st.spinner("Thinking..."):
                if coach_choice == "Claude":
                    response, error = get_claude_response(user_input, context)
                    provider = "Claude"
                elif coach_choice == "ChatGPT":
                    response, error = get_chatgpt_response(user_input, context)
                    provider = "ChatGPT"
                else:
                    response, error = get_gemini_response(user_input, context)
                    provider = "Gemini"
                
                if response:
                    st.session_state.coach_response = response
                    st.session_state.coach_provider = provider
                elif error:
                    st.session_state.coach_response = f"Could not connect to {provider}. Please try another coach or check API configuration."
                    st.session_state.coach_provider = "Error"
            
            st.rerun()
    
    if st.session_state.get("coach_response"):
        st.markdown(f'<div class="coach-response">{st.session_state.coach_response}</div>', unsafe_allow_html=True)
        if st.session_state.get("coach_provider") and st.session_state.coach_provider != "Error":
            st.markdown(f'<div class="coach-provider">Response from {st.session_state.coach_provider}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Account creation section
    st.markdown("""
    <div class="account-section">
        <div class="account-title">Save your results</div>
        <div class="account-subtitle">Create an account to track your progress over time</div>
        <div class="account-benefits">
            <div class="account-benefit">Save and revisit your career matches</div>
            <div class="account-benefit">Track your 4-week sprint progress</div>
            <div class="account-benefit">Get updated recommendations as you grow</div>
            <div class="account-benefit">Access all three AI coaches anytime</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Create free account", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()
    
    # Save session
    save_session({
        "timestamp": datetime.utcnow().isoformat(),
        "answers": answers,
        "top_match": top_match['career']['title'],
        "match_pct": top_match['match'],
        "strengths": strengths,
        "gaps": gaps,
        "coach_response": st.session_state.get("coach_response"),
        "coach_provider": st.session_state.get("coach_provider"),
    })
    
    st.markdown('<p class="footer-note">Share this with a mentor or colleague. Ask: what feels right?</p>', unsafe_allow_html=True)
    
    if st.button("Start over", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# =============================================================================
# MAIN
# =============================================================================

def main():
    step = st.session_state.get("step", "landing")
    
    if step == "landing":
        render_landing()
    elif step == "questions":
        render_questions()
    elif step == "results":
        render_results()

if __name__ == "__main__":
    main()
