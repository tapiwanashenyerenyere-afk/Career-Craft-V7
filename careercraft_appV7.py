"""
CareerCraft – Warm, Human-Centered Career Tool
Typeform-style one-question-at-a-time flow
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

# Page config
st.set_page_config(
    page_title="CareerCraft",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# DATA - No emojis, human language
# =============================================================================

SKILL_SECTIONS = [
    {
        "id": "thinking",
        "name": "Thinking",
        "intro": "Let's start with how you think and solve problems.",
        "skills": [
            {"name": "Problem solving", "question": "How often do you work through complex problems?"},
            {"name": "Learning quickly", "question": "How quickly do you pick up new concepts and skills?"},
            {"name": "Analytical thinking", "question": "How often do you analyze information to find patterns?"},
        ]
    },
    {
        "id": "technical",
        "name": "Technical",
        "intro": "Now let's look at your technical side.",
        "skills": [
            {"name": "Working with data", "question": "How comfortable are you working with spreadsheets and data?"},
            {"name": "Digital tools", "question": "How easily do you learn new software and tools?"},
            {"name": "Building systems", "question": "How often do you create processes or workflows?"},
        ]
    },
    {
        "id": "people",
        "name": "People",
        "intro": "Let's explore how you work with others.",
        "skills": [
            {"name": "Explaining ideas", "question": "How clearly can you explain complex ideas to others?"},
            {"name": "Supporting others", "question": "How naturally do you help and mentor teammates?"},
            {"name": "Leading people", "question": "How comfortable are you leading a group or project?"},
        ]
    },
    {
        "id": "delivery",
        "name": "Delivery",
        "intro": "Finally, let's see how you get things done.",
        "skills": [
            {"name": "Finishing tasks", "question": "How reliably do you complete what you start?"},
            {"name": "Managing time", "question": "How well do you juggle competing priorities?"},
            {"name": "Handling pressure", "question": "How do you perform when deadlines are tight?"},
        ]
    }
]

SKILL_LEVELS = [
    {"label": "Rarely", "value": 20},
    {"label": "Sometimes", "value": 45},
    {"label": "Often", "value": 70},
    {"label": "Daily", "value": 95},
]

CAREERS = [
    {"id": "pm", "title": "Product Manager", "subtitle": "Shape what gets built", "range": "$95k–$180k", "p50": 140000},
    {"id": "dev", "title": "Software Developer", "subtitle": "Build and create", "range": "$80k–$200k", "p50": 132000},
    {"id": "data", "title": "Data Analyst", "subtitle": "Find insights in numbers", "range": "$65k–$130k", "p50": 85000},
    {"id": "ux", "title": "UX Designer", "subtitle": "Design for humans", "range": "$70k–$150k", "p50": 98000},
    {"id": "marketing", "title": "Marketing Manager", "subtitle": "Tell compelling stories", "range": "$75k–$160k", "p50": 110000},
    {"id": "consultant", "title": "Consultant", "subtitle": "Solve business problems", "range": "$80k–$170k", "p50": 99000},
]

# =============================================================================
# CUSTOM CSS - Warm, high contrast, human
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,600&family=DM+Sans:wght@400;500;600&display=swap');
    
    /* Hide Streamlit chrome */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    
    /* Base */
    .stApp {
        background: #FBF8F3;
        font-family: 'DM Sans', -apple-system, sans-serif;
    }
    
    .main .block-container {
        padding: 2rem 1rem 4rem;
        max-width: 640px;
    }
    
    /* Typography */
    h1, h2, h3, h4 {
        font-family: 'Fraunces', Georgia, serif !important;
        color: #1F2421 !important;
        font-weight: 600 !important;
    }
    
    p, span, div {
        color: #374151;
    }
    
    /* Logo */
    .logo {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 2rem;
    }
    
    .logo-mark {
        width: 36px;
        height: 36px;
        background: #4A6741;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.1rem;
    }
    
    .logo-text {
        font-family: 'Fraunces', serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #1F2421;
    }
    
    /* Progress dots */
    .progress-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2.5rem;
    }
    
    .progress-dots {
        display: flex;
        gap: 0.4rem;
    }
    
    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #E5E7EB;
        transition: all 0.3s ease;
    }
    
    .dot.done {
        background: #4A6741;
    }
    
    .dot.active {
        background: #4A6741;
        transform: scale(1.3);
        box-shadow: 0 0 0 4px rgba(74, 103, 65, 0.15);
    }
    
    .progress-label {
        font-size: 0.85rem;
        color: #6B7280;
        font-weight: 500;
    }
    
    /* Question card */
    .question-container {
        animation: fadeUp 0.4s ease-out;
    }
    
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .question-intro {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 0.75rem;
        font-style: italic;
    }
    
    .question-text {
        font-family: 'Fraunces', Georgia, serif;
        font-size: 1.75rem;
        font-weight: 600;
        color: #1F2421;
        line-height: 1.35;
        margin-bottom: 2rem;
    }
    
    /* Hero section */
    .hero {
        text-align: center;
        padding: 3rem 0;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: white;
        border: 1px solid #E5E7EB;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .hero-dot {
        width: 8px;
        height: 8px;
        background: #22C55E;
        border-radius: 50%;
    }
    
    .hero-title {
        font-family: 'Fraunces', Georgia, serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #1F2421;
        line-height: 1.2;
        margin-bottom: 1rem;
    }
    
    .hero-title em {
        font-style: italic;
        color: #4A6741;
    }
    
    .hero-sub {
        font-size: 1.1rem;
        color: #4B5563;
        line-height: 1.6;
        max-width: 500px;
        margin: 0 auto 2rem;
    }
    
    /* Steps */
    .steps {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2.5rem 0;
        flex-wrap: wrap;
    }
    
    .step {
        text-align: center;
        max-width: 160px;
    }
    
    .step-num {
        width: 44px;
        height: 44px;
        background: #4A6741;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 0 auto 0.75rem;
    }
    
    .step-title {
        font-weight: 600;
        color: #1F2421;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
    }
    
    .step-desc {
        font-size: 0.8rem;
        color: #6B7280;
        line-height: 1.4;
    }
    
    /* Entry cards */
    .entry-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .entry-card {
        background: white;
        border-radius: 16px;
        padding: 1.75rem 1.25rem;
        text-align: center;
        border: 2px solid #E5E7EB;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    
    .entry-card:hover {
        border-color: #4A6741;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    
    .entry-icon {
        width: 56px;
        height: 56px;
        background: #E8EFE6;
        border-radius: 12px;
        margin: 0 auto 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: #4A6741;
    }
    
    .entry-title {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1F2421;
        margin-bottom: 0.5rem;
    }
    
    .entry-body {
        font-size: 0.9rem;
        color: #6B7280;
        line-height: 1.45;
        margin-bottom: 0.75rem;
    }
    
    .entry-hint {
        font-size: 0.8rem;
        color: #C75B39;
        font-weight: 500;
    }
    
    /* Career grid */
    .career-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .career-card {
        background: white;
        border: 2px solid #E5E7EB;
        border-radius: 14px;
        padding: 1.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .career-card:hover {
        border-color: #4A6741;
    }
    
    .career-card.selected {
        border-color: #4A6741;
        background: #F0FDF4;
    }
    
    .career-title {
        font-family: 'Fraunces', serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: #1F2421;
        margin-bottom: 0.25rem;
    }
    
    .career-subtitle {
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }
    
    .career-salary {
        font-size: 0.8rem;
        color: #4A6741;
        font-weight: 600;
    }
    
    /* Results page */
    .results-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .results-title {
        font-family: 'Fraunces', serif;
        font-size: 1.75rem;
        color: #1F2421;
        margin-bottom: 0.5rem;
    }
    
    .results-sub {
        color: #6B7280;
        font-size: 1rem;
    }
    
    /* Result cards */
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }
    
    .result-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6B7280;
        margin-bottom: 0.75rem;
        font-weight: 600;
    }
    
    .pill {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .pill-green {
        background: #DCFCE7;
        color: #166534;
    }
    
    .pill-amber {
        background: #FEF3C7;
        color: #92400E;
    }
    
    /* Direction cards */
    .direction-card {
        background: white;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        position: relative;
    }
    
    .direction-primary {
        border-color: #4A6741;
        background: linear-gradient(135deg, #F0FDF4 0%, white 100%);
    }
    
    .direction-lateral {
        border-color: #3B82F6;
        background: linear-gradient(135deg, #EFF6FF 0%, white 100%);
    }
    
    .direction-stretch {
        border-color: #F59E0B;
        background: linear-gradient(135deg, #FFFBEB 0%, white 100%);
    }
    
    .direction-type {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    
    .direction-primary .direction-type { color: #166534; }
    .direction-lateral .direction-type { color: #1D4ED8; }
    .direction-stretch .direction-type { color: #B45309; }
    
    .direction-title {
        font-family: 'Fraunces', serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: #1F2421;
        margin-bottom: 0.35rem;
    }
    
    .direction-meta {
        font-size: 0.9rem;
        color: #4B5563;
    }
    
    .direction-match {
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
    }
    
    .direction-primary .direction-match {
        background: #DCFCE7;
        color: #166534;
    }
    
    .direction-lateral .direction-match,
    .direction-stretch .direction-match {
        background: #FEF3C7;
        color: #92400E;
    }
    
    /* Timeline */
    .timeline-card {
        background: #1F2421;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1.5rem 0;
    }
    
    .timeline-header {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9CA3AF;
        margin-bottom: 1.25rem;
        font-weight: 600;
    }
    
    .timeline {
        position: relative;
        padding-left: 1.75rem;
    }
    
    .timeline::before {
        content: '';
        position: absolute;
        left: 5px;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #4A6741, #3B82F6, #C75B39);
        border-radius: 2px;
    }
    
    .tl-item {
        position: relative;
        margin-bottom: 1.25rem;
        padding: 0.9rem;
        background: rgba(255,255,255,0.06);
        border-radius: 10px;
    }
    
    .tl-item::before {
        content: '';
        position: absolute;
        left: -1.4rem;
        top: 1rem;
        width: 11px;
        height: 11px;
        border-radius: 50%;
    }
    
    .tl-direction::before { background: #4A6741; }
    .tl-phase::before { background: #3B82F6; }
    .tl-sprint::before { background: #C75B39; }
    
    .tl-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    
    .tl-direction .tl-label { color: #86EFAC; }
    .tl-phase .tl-label { color: #93C5FD; }
    .tl-sprint .tl-label { color: #FCA5A5; }
    
    .tl-title {
        font-family: 'Fraunces', serif;
        font-size: 1rem;
        color: #F9FAFB;
        line-height: 1.4;
    }
    
    .tl-body {
        font-size: 0.85rem;
        color: #D1D5DB;
        margin-top: 0.3rem;
        line-height: 1.45;
    }
    
    /* Coach */
    .coach-card {
        background: white;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1.5rem 0;
        border: 1px solid #E5E7EB;
    }
    
    .coach-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .coach-avatar {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #4A6741, #6B8F62);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
    }
    
    .coach-name {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1F2421;
    }
    
    .coach-role {
        font-size: 0.85rem;
        color: #6B7280;
    }
    
    .coach-response {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-top: 1rem;
        font-size: 0.95rem;
        line-height: 1.7;
        color: #1F2421;
    }
    
    .coach-provider {
        font-size: 0.8rem;
        color: #6B7280;
        margin-top: 0.75rem;
    }
    
    /* Integration */
    .integration-card {
        background: #F9FAFB;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1.5rem 0;
        text-align: center;
    }
    
    .integration-title {
        font-family: 'Fraunces', serif;
        font-size: 1.15rem;
        color: #1F2421;
        margin-bottom: 0.5rem;
    }
    
    .integration-sub {
        font-size: 0.9rem;
        color: #6B7280;
        margin-bottom: 1.25rem;
    }
    
    /* Streamlit overrides */
    .stButton > button {
        background: #4A6741 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
        box-shadow: 0 4px 12px rgba(74, 103, 65, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #3d5636 !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #374151 !important;
        border: 2px solid #E5E7EB !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: #4A6741 !important;
        color: #4A6741 !important;
        background: #F0FDF4 !important;
    }
    
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #E5E7EB !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1rem !important;
        padding: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #4A6741 !important;
        box-shadow: 0 0 0 1px #4A6741 !important;
    }
    
    .stLinkButton > a {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
    }
    
    /* Footer note */
    .footer-note {
        text-align: center;
        font-size: 0.85rem;
        color: #9CA3AF;
        margin-top: 2rem;
        font-style: italic;
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

def get_strengths_and_gaps(skills):
    if not skills:
        return ["Problem solving", "Explaining ideas"], ["Working with data"]
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    strengths = [s for s, v in sorted_skills[:3] if v >= 60]
    gaps = [s for s, v in sorted_skills if v <= 40][:2]
    if not strengths:
        strengths = [sorted_skills[0][0], sorted_skills[1][0]] if len(sorted_skills) >= 2 else ["Problem solving"]
    if not gaps:
        gaps = [sorted_skills[-1][0]] if sorted_skills else ["Technical skills"]
    return strengths, gaps

def generate_ai_prompt(strengths, gaps, direction):
    return f"""I just completed a CareerCheck assessment. Here are my results:

My Strengths: {', '.join(strengths)}
My Growth Areas: {', '.join(gaps)}
Direction I'm Exploring: {direction}
My 4-Week Sprint: Talk to 2 {direction}s, start 1 mini project, sample 1 course

Can you help me:
1. Think through whether this direction makes sense given my strengths
2. Suggest specific ways to close my skill gaps
3. Give me concrete next steps for my 4-week sprint
4. Ask me questions to better understand my situation"""

def get_ai_response(user_msg, context):
    anthropic_key = get_secret("ANTHROPIC_API_KEY")
    openai_key = get_secret("OPENAI_API_KEY")
    provider = get_secret("LLM_PROVIDER", "anthropic").lower()
    
    system = """You are a gentle, honest career coach. Help people think through career decisions with:
1. What matters most right now
2. How to frame the next 3-6 months
3. 1-3 concrete, low-risk experiments to try

Keep responses under 300 words. Be warm but direct. Don't promise outcomes. Speak like a wise friend."""
    
    user_prompt = f"""Context:
- Direction: {context.get('direction', 'exploring options')}
- Strengths: {', '.join(context.get('strengths', []))}
- Growth areas: {', '.join(context.get('gaps', []))}

Their question: {user_msg}

Give them practical, warm guidance."""

    if provider == "anthropic" and anthropic_key and ANTHROPIC_AVAILABLE:
        try:
            client = anthropic.Anthropic(api_key=anthropic_key)
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=system,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return resp.content[0].text.strip(), "claude"
        except:
            pass
    
    if openai_key and OPENAI_AVAILABLE:
        try:
            client = OpenAI(api_key=openai_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=500,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return resp.choices[0].message.content.strip(), "openai"
        except:
            pass
    
    # Fallback
    strengths_text = ', '.join(context.get('strengths', ['your strengths']))
    return f"""Here's how I'd approach the next few months:

Build on what works. {strengths_text} are your foundation—look for opportunities that use these daily.

Test before committing. Treat your target role as a hypothesis. Have 2-3 conversations with people in that role. Ask: what does a typical week look like?

One small experiment. Pick something you can do in the next 4 weeks: take a short course, start a side project, or volunteer for a relevant task.

Talk it through. Share this with someone you trust. Ask them: what feels right? What's missing?

The goal isn't perfection—it's learning what actually fits you.""", "fallback"

# =============================================================================
# SESSION STATE
# =============================================================================

if "step" not in st.session_state:
    st.session_state.step = "landing"
    st.session_state.entry_mode = None
    st.session_state.skill_section = 0
    st.session_state.skill_question = 0
    st.session_state.skills = {}
    st.session_state.careers = []
    st.session_state.coach_response = None
    st.session_state.coach_provider = None
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")

# Ensure all keys exist
for key in ["coach_provider", "coach_response", "skill_section", "skill_question"]:
    if key not in st.session_state:
        st.session_state[key] = None if "response" in key or "provider" in key else 0

# =============================================================================
# LOGO
# =============================================================================

def render_logo():
    st.markdown("""
    <div class="logo">
        <div class="logo-mark">◆</div>
        <div class="logo-text">CareerCraft</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# LANDING PAGE
# =============================================================================

def render_landing():
    render_logo()
    
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">
            <span class="hero-dot"></span>
            Free career tool · 7 minutes
        </div>
        <h1 class="hero-title">Get <em>clarity</em> on your career.<br>Not just another quiz.</h1>
        <p class="hero-sub">
            Map your skills to real salary data and walk away with a clear next step.
            Use it before talking to a mentor or making a big decision.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="steps">
        <div class="step">
            <div class="step-num">1</div>
            <div class="step-title">Map your skills</div>
            <div class="step-desc">12 quick questions about what you do well</div>
        </div>
        <div class="step">
            <div class="step-num">2</div>
            <div class="step-title">See directions</div>
            <div class="step-desc">3 career paths with salary data</div>
        </div>
        <div class="step">
            <div class="step-num">3</div>
            <div class="step-title">Get your sprint</div>
            <div class="step-desc">A 4-week experiment to try</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="entry-grid">
        <div class="entry-card" id="skills-card">
            <div class="entry-icon">◎</div>
            <div class="entry-title">Start from my skills</div>
            <div class="entry-body">Map what you're good at. We'll suggest directions that fit.</div>
            <div class="entry-hint">Best if you're unsure where to go</div>
        </div>
        <div class="entry-card" id="career-card">
            <div class="entry-icon">↗</div>
            <div class="entry-title">Start from a career</div>
            <div class="entry-body">Pick roles you're curious about. We'll show your gaps.</div>
            <div class="entry-hint">Best if you have directions in mind</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start from skills", use_container_width=True):
            st.session_state.step = "skills"
            st.session_state.entry_mode = "skills"
            st.session_state.skill_section = 0
            st.session_state.skill_question = 0
            st.rerun()
    with col2:
        if st.button("Start from career", use_container_width=True):
            st.session_state.step = "career"
            st.session_state.entry_mode = "career"
            st.rerun()
    
    st.markdown('<p class="footer-note">No signup required. This is decision support, not prophecy.</p>', unsafe_allow_html=True)

# =============================================================================
# SKILLS - TYPEFORM STYLE (ONE AT A TIME)
# =============================================================================

def render_skills():
    render_logo()
    
    section_idx = st.session_state.skill_section
    question_idx = st.session_state.skill_question
    
    # Calculate overall progress
    total_questions = sum(len(s["skills"]) for s in SKILL_SECTIONS)
    questions_before = sum(len(SKILL_SECTIONS[i]["skills"]) for i in range(section_idx))
    current_question_num = questions_before + question_idx + 1
    
    section = SKILL_SECTIONS[section_idx]
    skill_data = section["skills"][question_idx]
    skill_name = skill_data["name"]
    
    # Progress dots (one per section)
    dots_html = ""
    for i, s in enumerate(SKILL_SECTIONS):
        if i < section_idx:
            dots_html += '<span class="dot done"></span>'
        elif i == section_idx:
            dots_html += '<span class="dot active"></span>'
        else:
            dots_html += '<span class="dot"></span>'
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-dots">{dots_html}</div>
        <div class="progress-label">{section['name']} · Question {current_question_num} of {total_questions}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show intro on first question of each section
    intro_text = section["intro"] if question_idx == 0 else ""
    
    st.markdown(f"""
    <div class="question-container">
        <p class="question-intro">{intro_text}</p>
        <h2 class="question-text">{skill_data['question']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Answer buttons
    current_value = st.session_state.skills.get(skill_name, None)
    
    cols = st.columns(4)
    for i, level in enumerate(SKILL_LEVELS):
        with cols[i]:
            is_selected = current_value == level["value"]
            btn_label = f"✓ {level['label']}" if is_selected else level["label"]
            btn_type = "primary" if is_selected else "secondary"
            
            if st.button(btn_label, key=f"skill_{skill_name}_{level['value']}", 
                        type=btn_type, use_container_width=True):
                st.session_state.skills[skill_name] = level["value"]
                st.rerun()
    
    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_question_num > 1:
            if st.button("← Back", type="secondary", use_container_width=True):
                if question_idx > 0:
                    st.session_state.skill_question -= 1
                else:
                    st.session_state.skill_section -= 1
                    st.session_state.skill_question = len(SKILL_SECTIONS[st.session_state.skill_section]["skills"]) - 1
                st.rerun()
        else:
            if st.button("← Exit", type="secondary", use_container_width=True):
                st.session_state.step = "landing"
                st.rerun()
    
    with col3:
        can_continue = current_value is not None
        
        is_last = (section_idx == len(SKILL_SECTIONS) - 1 and 
                   question_idx == len(section["skills"]) - 1)
        
        if is_last:
            if st.button("See results →", disabled=not can_continue, use_container_width=True):
                st.session_state.step = "results"
                st.rerun()
        else:
            if st.button("Next →", disabled=not can_continue, use_container_width=True):
                if question_idx < len(section["skills"]) - 1:
                    st.session_state.skill_question += 1
                else:
                    st.session_state.skill_section += 1
                    st.session_state.skill_question = 0
                st.rerun()

# =============================================================================
# CAREER SELECTION
# =============================================================================

def render_career():
    render_logo()
    
    st.markdown("""
    <div class="progress-container">
        <div class="progress-dots">
            <span class="dot done"></span>
            <span class="dot active"></span>
            <span class="dot"></span>
        </div>
        <div class="progress-label">Careers</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="question-container">
        <p class="question-intro">Let's see what you're curious about.</p>
        <h2 class="question-text">Which careers interest you?</h2>
        <p style="color: #6B7280; margin-top: -1rem; margin-bottom: 1.5rem;">Pick 1-3 to explore</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Career grid
    cols = st.columns(2)
    for i, career in enumerate(CAREERS):
        with cols[i % 2]:
            selected = career["id"] in st.session_state.careers
            
            st.markdown(f"""
            <div class="career-card {'selected' if selected else ''}" style="margin-bottom: 0.5rem;">
                <div class="career-title">{career['title']}</div>
                <div class="career-subtitle">{career['subtitle']}</div>
                <div class="career-salary">{career['range']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            btn_label = "✓ Selected" if selected else "Select"
            btn_type = "primary" if selected else "secondary"
            if st.button(btn_label, key=f"career_{career['id']}", type=btn_type, use_container_width=True):
                if selected:
                    st.session_state.careers.remove(career["id"])
                elif len(st.session_state.careers) < 3:
                    st.session_state.careers.append(career["id"])
                st.rerun()
    
    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back", type="secondary", use_container_width=True):
            st.session_state.step = "landing"
            st.rerun()
    
    with col3:
        can_continue = len(st.session_state.careers) > 0
        if st.button("See results →", disabled=not can_continue, use_container_width=True):
            st.session_state.step = "results"
            st.rerun()

# =============================================================================
# RESULTS
# =============================================================================

def render_results():
    render_logo()
    
    strengths, gaps = get_strengths_and_gaps(st.session_state.skills)
    
    st.markdown("""
    <div class="results-header">
        <h1 class="results-title">Your CareerCheck Results</h1>
        <p class="results-sub">Here's what we found based on your inputs</p>
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
    
    # Directions
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-label">Career Directions</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="direction-card direction-primary">
        <div class="direction-type">Best match</div>
        <div class="direction-title">Product Manager</div>
        <div class="direction-meta">$95k–$180k · Shape what gets built</div>
        <div class="direction-match">85%</div>
    </div>
    <div class="direction-card direction-lateral">
        <div class="direction-type">Lateral move</div>
        <div class="direction-title">Business Analyst</div>
        <div class="direction-meta">$70k–$130k · Bridge business and tech</div>
        <div class="direction-match">72%</div>
    </div>
    <div class="direction-card direction-stretch">
        <div class="direction-type">Stretch goal</div>
        <div class="direction-title">Data Scientist</div>
        <div class="direction-meta">$90k–$165k · Find insights in numbers</div>
        <div class="direction-match">55%</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Timeline
    st.markdown("""
    <div class="timeline-card">
        <div class="timeline-header">Your Path Forward</div>
        <div class="timeline">
            <div class="tl-item tl-direction">
                <div class="tl-label">6-12 Month Direction</div>
                <div class="tl-title">Explore Product Manager while maintaining stable income</div>
            </div>
            <div class="tl-item tl-phase">
                <div class="tl-label">3-Month Phase</div>
                <div class="tl-title">Exploration & Foundations</div>
                <div class="tl-body">Test if this direction feels right through real conversations and small experiments.</div>
            </div>
            <div class="tl-item tl-sprint">
                <div class="tl-label">4-Week Sprint</div>
                <div class="tl-title">Talk to 2 PMs, start 1 project, sample 1 course</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Coach
    st.markdown('<div class="coach-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="coach-header">
        <div class="coach-avatar">C</div>
        <div>
            <div class="coach-name">Career Coach</div>
            <div class="coach-role">Ask a question about your results</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    user_input = st.text_area(
        "What's on your mind?",
        placeholder="What feels unclear or scary about making this change?",
        key="coach_input",
        label_visibility="collapsed"
    )
    
    if st.button("Get guidance", type="primary"):
        if user_input.strip():
            with st.spinner("Thinking..."):
                context = {
                    "direction": "Product Manager",
                    "strengths": strengths,
                    "gaps": gaps,
                }
                response, provider = get_ai_response(user_input, context)
                st.session_state.coach_response = response
                st.session_state.coach_provider = provider
            st.rerun()
    
    if st.session_state.get("coach_response"):
        provider = st.session_state.get("coach_provider", "")
        provider_text = ""
        if provider == "claude":
            provider_text = "Powered by Claude"
        elif provider == "openai":
            provider_text = "Powered by ChatGPT"
        
        st.markdown(f'<div class="coach-response">{st.session_state.coach_response}</div>', unsafe_allow_html=True)
        if provider_text:
            st.markdown(f'<div class="coach-provider">{provider_text}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Continue with ChatGPT/Claude
    st.markdown('<div class="integration-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="integration-title">Continue the conversation</div>
    <div class="integration-sub">Take your results to ChatGPT or Claude for deeper exploration</div>
    """, unsafe_allow_html=True)
    
    prompt = generate_ai_prompt(strengths, gaps, "Product Manager")
    st.code(prompt, language=None)
    st.caption("Copy this prompt, then click below to open your preferred AI")
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("Open Claude", "https://claude.ai/new", use_container_width=True)
    with col2:
        st.link_button("Open ChatGPT", "https://chat.openai.com/", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Save session
    save_session({
        "timestamp": datetime.utcnow().isoformat(),
        "entry_mode": st.session_state.entry_mode,
        "skills": st.session_state.skills,
        "careers": st.session_state.careers,
        "strengths": strengths,
        "gaps": gaps,
        "coach_response": st.session_state.get("coach_response"),
        "coach_provider": st.session_state.get("coach_provider"),
    })
    
    # Footer
    st.markdown('<p class="footer-note">Take this to a mentor or friend. Ask: what feels true? What\'s missing?</p>', unsafe_allow_html=True)
    
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
    elif step == "skills":
        render_skills()
    elif step == "career":
        render_career()
    elif step == "results":
        render_results()

if __name__ == "__main__":
    main()
