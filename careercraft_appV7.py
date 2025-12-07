"""
CareerCraft – Polished Streamlit App
With ChatGPT/Claude integration buttons
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import urllib.parse

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
    page_title="CareerCraft – Know What Your Skills Are Worth",
    page_icon="✧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=DM+Sans:wght@400;500;600&display=swap');
    
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    
    .stApp {
        background: #FBF8F3;
        font-family: 'DM Sans', sans-serif;
    }
    
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }
    
    h1, h2, h3 {
        font-family: 'Fraunces', Georgia, serif !important;
        color: #1F2421 !important;
    }
    
    /* Hero */
    .hero-box {
        text-align: center;
        padding: 2rem 1rem 1.5rem;
        max-width: 700px;
        margin: 0 auto;
    }
    
    .trust-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: white;
        border: 1px solid rgba(0,0,0,0.08);
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-size: 0.85rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .trust-dot {
        width: 8px;
        height: 8px;
        background: #22C55E;
        border-radius: 50%;
    }
    
    .hero-title {
        font-family: 'Fraunces', Georgia, serif !important;
        font-size: 2.25rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 1rem;
        color: #1F2421;
    }
    
    .hero-title em {
        font-style: italic;
        color: #4A6741;
    }
    
    .hero-sub {
        font-size: 1.05rem;
        color: #4B5563;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }
    
    .hero-note {
        font-size: 0.8rem;
        color: #9CA3AF;
        margin-top: 1.5rem;
    }
    
    /* How it works steps */
    .steps-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .step-item {
        text-align: center;
        max-width: 200px;
    }
    
    .step-number {
        width: 40px;
        height: 40px;
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
    }
    
    .step-desc {
        font-size: 0.85rem;
        color: #6B7280;
        line-height: 1.4;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    
    .card-dark {
        background: #1F2421;
        color: #E5E7EB;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .card-sage {
        background: linear-gradient(135deg, #E8EFE6, #F5F0E8);
        border: 1px solid rgba(74, 103, 65, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Entry cards */
    .entry-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.25rem;
        margin: 1.5rem 0;
    }
    
    .entry-card {
        background: #1F2421;
        color: white;
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
    }
    
    .entry-icon { font-size: 2.5rem; margin-bottom: 1rem; }
    .entry-title { font-family: 'Fraunces', serif; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem; color: white; }
    .entry-body { font-size: 0.9rem; color: #D1D5DB; line-height: 1.5; margin-bottom: 1rem; }
    .entry-cta { font-size: 0.85rem; color: #C75B39; font-weight: 500; }
    
    /* Integration banner */
    .integration-banner {
        background: linear-gradient(135deg, #E8EFE6, #F0F9FF);
        border: 1px solid rgba(74, 103, 65, 0.2);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .integration-text {
        flex: 1;
        font-size: 0.9rem;
        color: #374151;
    }
    
    .integration-logos {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .integration-logo {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
    }
    
    .logo-claude { background: #D97706; color: white; }
    .logo-gpt { background: #10A37F; color: white; }
    
    /* Progress */
    .progress-box {
        margin-bottom: 1.5rem;
    }
    
    .progress-steps {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
        color: #9CA3AF;
    }
    
    .progress-steps .active { color: #4A6741; font-weight: 600; }
    .progress-steps .done { color: #4A6741; }
    
    .progress-track {
        height: 4px;
        background: #E5E7EB;
        border-radius: 2px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4A6741, #C75B39);
        border-radius: 2px;
    }
    
    /* Pills */
    .pill {
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    
    .pill-sage { background: #E8EFE6; color: #2D4A27; }
    .pill-ready { background: #DCFCE7; color: #166534; }
    .pill-stretch { background: #FEF3C7; color: #92400E; }
    
    /* Direction cards - FIXED COLORS */
    .dir-card {
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
    }
    
    .dir-deeper { 
        background: #E8EFE6; 
        border-color: #4A6741; 
    }
    .dir-lateral { 
        background: #EFF6FF; 
        border-color: #3B82F6; 
    }
    .dir-stretch { 
        background: #FEF3C7; 
        border-color: #F59E0B; 
    }
    
    .dir-title { 
        font-weight: 600; 
        margin-bottom: 0.25rem; 
        color: #1F2421;
        font-size: 1rem;
    }
    .dir-meta { 
        font-size: 0.9rem; 
        color: #374151; 
    }
    
    .match-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .match-ready { background: #DCFCE7; color: #166534; }
    .match-stretch { background: #FEF3C7; color: #92400E; }
    
    /* Timeline */
    .timeline {
        position: relative;
        padding-left: 2rem;
        margin: 1.5rem 0;
    }
    
    .timeline::before {
        content: '';
        position: absolute;
        left: 0.4rem;
        top: 0.5rem;
        bottom: 0.5rem;
        width: 3px;
        background: linear-gradient(180deg, #4A6741, #3B82F6, #C75B39);
        border-radius: 2px;
    }
    
    .tl-item {
        position: relative;
        margin-bottom: 1.25rem;
        padding: 1rem;
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
    }
    
    .tl-item::before {
        content: '';
        position: absolute;
        left: -1.6rem;
        top: 1.1rem;
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    
    .tl-direction::before { background: #4A6741; }
    .tl-phase::before { background: #3B82F6; }
    .tl-sprint::before { background: #C75B39; }
    
    .tl-label {
        font-size: 0.7rem;
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
        color: white;
    }
    
    .tl-body {
        font-size: 0.85rem;
        color: #D1D5DB;
        margin-top: 0.25rem;
    }
    
    /* Coach - FIXED */
    .coach-box {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(0,0,0,0.08);
        margin-top: 1.5rem;
    }
    
    .coach-header {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1F2421;
    }
    
    .coach-sub {
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 1rem;
    }
    
    .coach-response {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 12px;
        padding: 1.25rem;
        font-size: 0.9rem;
        line-height: 1.7;
        margin-top: 1rem;
        color: #1F2421;
    }
    
    /* Buttons - FIXED: Different styles for selected vs unselected */
    .stButton > button {
        background: #4A6741 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(74, 103, 65, 0.2) !important;
    }
    
    .stButton > button:hover {
        background: #3d5636 !important;
    }
    
    /* Secondary buttons (skill options not selected) */
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #374151 !important;
        border: 1px solid #D1D5DB !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: #4A6741 !important;
        color: #4A6741 !important;
    }
    
    /* Text areas */
    .stTextArea textarea {
        border-radius: 12px !important;
        border-color: #E5E7EB !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #4A6741 !important;
        box-shadow: 0 0 0 1px #4A6741 !important;
    }
    
    /* Link buttons */
    .stLinkButton > a {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA
# =============================================================================

SKILL_GROUPS = {
    "🧠 Thinking": ["Problem solving", "Learning quickly", "Analytical thinking"],
    "⚙️ Technical": ["Working with data", "Digital tools", "Building systems"],
    "💬 People": ["Explaining ideas", "Supporting others", "Leading people"],
    "🚀 Delivery": ["Finishing tasks", "Managing time", "Handling pressure"]
}

CAREERS = [
    {"id": "pm", "title": "Product Manager", "icon": "🎯", "range": "$95k–$180k", "p50": 140000},
    {"id": "dev", "title": "Software Developer", "icon": "💻", "range": "$80k–$200k", "p50": 132000},
    {"id": "data", "title": "Data Analyst", "icon": "📊", "range": "$65k–$130k", "p50": 85000},
    {"id": "ux", "title": "UX Designer", "icon": "🎨", "range": "$70k–$150k", "p50": 98000},
    {"id": "marketing", "title": "Marketing Manager", "icon": "📈", "range": "$75k–$160k", "p50": 110000},
    {"id": "consultant", "title": "Consultant", "icon": "💼", "range": "$80k–$170k", "p50": 99000},
]

# =============================================================================
# HELPERS
# =============================================================================

def get_secret(key, default=None):
    try:
        return dict(st.secrets).get(key, default)
    except:
        return default

def ensure_data_dir():
    Path("careercraft_data").mkdir(exist_ok=True)

def save_session(data):
    try:
        ensure_data_dir()
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        sid = st.session_state.get("session_id", "unknown")
        with open(f"careercraft_data/session_{ts}_{sid[:8]}.json", "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def get_strengths_and_gaps(skills):
    if not skills:
        return [], []
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    strengths = [s for s, v in sorted_skills[:3] if v >= 60]
    gaps = [s for s, v in sorted_skills if v <= 40][:2]
    return strengths, gaps

def get_readiness(gaps_count):
    if gaps_count <= 1:
        return "Ready", "match-ready"
    elif gaps_count <= 3:
        return "Stretch", "match-stretch"
    return "Long-shot", "match-stretch"

def generate_ai_prompt(strengths, gaps, direction="Product Manager"):
    """Generate a prompt users can paste into ChatGPT or Claude"""
    return f"""I just completed a CareerCheck assessment. Here are my results:

**My Strengths:** {', '.join(strengths) if strengths else 'Problem solving, Communication'}

**My Growth Areas:** {', '.join(gaps) if gaps else 'Data skills, Technical tools'}

**Direction I'm Exploring:** {direction}

**My 4-Week Sprint:** Talk to 2 {direction}s, start 1 mini project, sample 1 course

Can you help me:
1. Think through whether this direction makes sense given my strengths
2. Suggest specific ways to close my skill gaps
3. Give me concrete next steps for my 4-week sprint
4. Ask me questions to better understand my situation"""

# =============================================================================
# AI COACH (built-in)
# =============================================================================

def get_ai_response(user_msg, context):
    anthropic_key = get_secret("ANTHROPIC_API_KEY")
    openai_key = get_secret("OPENAI_API_KEY")
    provider = get_secret("LLM_PROVIDER", "anthropic").lower()
    
    system = """You are a gentle, honest career coach. Help people think through career decisions with:
1. What matters most right now
2. How to frame the next 3-6 months
3. 1-3 concrete, low-risk experiments to try

Keep responses under 300 words. Be warm but direct. Don't promise outcomes."""
    
    user_prompt = f"""Context about the user:
- Direction: {context.get('direction', 'exploring options')}
- Strengths: {', '.join(context.get('strengths', ['problem solving']))}
- Gaps: {', '.join(context.get('gaps', ['some skills']))}
- Readiness: {context.get('readiness', 'Stretch')}

Their question/concern: {user_msg}

Give them practical guidance."""

    # Try Claude first
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
        except Exception as e:
            pass
    
    # Try OpenAI
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
    strengths = ', '.join(context.get('strengths', ['your existing skills']))
    fallback = f"""Here's how I'd approach the next few months:

**1. Build on what works.** {strengths} are your foundation—look for opportunities that use these daily.

**2. Test before committing.** Treat your target role as a hypothesis. Have 2-3 conversations with people in that role. Ask: what does a typical week look like? What surprised you about this work?

**3. One small experiment.** Pick something you can do in the next 4 weeks: take a short course, start a side project, or volunteer for a relevant task at work.

**4. Talk it through.** Share this with someone you trust. Ask them: what feels right? What's missing?

The goal isn't perfection—it's learning what actually fits you."""
    return fallback, "fallback"

# =============================================================================
# SESSION STATE - FIXED: Initialize all keys
# =============================================================================

if "step" not in st.session_state:
    st.session_state.step = "landing"
    st.session_state.skills = {}
    st.session_state.entry_mode = None
    st.session_state.careers = []
    st.session_state.coach_response = None
    st.session_state.coach_provider = None  # FIXED: Initialize this
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")

# Ensure coach_provider exists (for existing sessions)
if "coach_provider" not in st.session_state:
    st.session_state.coach_provider = None

# =============================================================================
# SCREENS
# =============================================================================

def render_landing():
    st.markdown("""
    <div class="hero-box">
        <div class="trust-badge">
            <span class="trust-dot"></span>
            Free career tool • ~7 minutes
        </div>
        <div class="hero-title">Get <em>clarity</em> on your career.<br>Not just another quiz.</div>
        <p class="hero-sub">
            CareerCraft turns your skills into salary ranges, skill gaps, and a clear next sprint.<br>
            Use it before you talk to a mentor, counsellor, or make a big decision.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # How it works steps
    st.markdown("""
    <div class="steps-container">
        <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-title">Map your skills</div>
            <div class="step-desc">Rate 12 skills across thinking, technical, people & delivery</div>
        </div>
        <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-title">See your directions</div>
            <div class="step-desc">Get 3 career paths with salary ranges and gap analysis</div>
        </div>
        <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-title">Get your sprint</div>
            <div class="step-desc">Leave with a 4-week experiment to test your hypothesis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Entry cards
    st.markdown("""
    <div class="entry-grid">
        <div class="entry-card">
            <div class="entry-icon">🎯</div>
            <div class="entry-title">Start from my skills</div>
            <div class="entry-body">Map what you're good at. We'll suggest directions that fit.</div>
            <div class="entry-cta">Best if you're unsure where to go</div>
        </div>
        <div class="entry-card">
            <div class="entry-icon">🧭</div>
            <div class="entry-title">Start from a career</div>
            <div class="entry-body">Pick roles you're curious about. We'll show your gaps.</div>
            <div class="entry-cta">Best if you have directions in mind</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 Start from skills", use_container_width=True):
            st.session_state.step = "skills"
            st.session_state.entry_mode = "skills"
            st.rerun()
    with col2:
        if st.button("🧭 Start from career", use_container_width=True):
            st.session_state.step = "career"
            st.session_state.entry_mode = "career"
            st.rerun()
    
    # Integration banner
    st.markdown("""
    <div class="integration-banner">
        <div class="integration-text">
            <strong>Continue the conversation:</strong> After your CareerCheck, take your results to ChatGPT or Claude for deeper exploration.
        </div>
        <div class="integration-logos">
            <div class="integration-logo logo-claude">C</div>
            <div class="integration-logo logo-gpt">G</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="hero-note">No signup required. This is decision support, not prophecy.</p>', unsafe_allow_html=True)


def render_skills():
    answered = len(st.session_state.skills)
    total = sum(len(v) for v in SKILL_GROUPS.values())
    pct = int((answered / total) * 50) + 25
    
    st.markdown(f"""
    <div class="progress-box">
        <div class="progress-steps">
            <span class="done">Entry</span>
            <span class="active">Skills</span>
            <span>Results</span>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back"):
            st.session_state.step = "landing"
            st.rerun()
    
    st.markdown("### Map your skills")
    st.markdown("How often does each skill show up in your work and life?")
    
    for group, skills in SKILL_GROUPS.items():
        st.markdown(f"**{group}**")
        for skill in skills:
            cols = st.columns([3, 1, 1, 1, 1])
            with cols[0]:
                st.markdown(f"<div style='padding:0.5rem 0; color:#1F2421;'>{skill}</div>", unsafe_allow_html=True)
            
            levels = [("Never", 20), ("Sometimes", 45), ("Often", 70), ("Weekly", 95)]
            current_value = st.session_state.skills.get(skill, 0)
            
            for i, (label, val) in enumerate(levels):
                with cols[i+1]:
                    # FIXED: Use different button types for selected vs not
                    is_selected = current_value == val
                    if is_selected:
                        # Selected - show as primary (green)
                        if st.button(f"✓ {label}", key=f"{skill}_{val}", type="primary", use_container_width=True):
                            pass  # Already selected
                    else:
                        # Not selected - show as secondary (white)
                        if st.button(label, key=f"{skill}_{val}", type="secondary", use_container_width=True):
                            st.session_state.skills[skill] = val
                            st.rerun()
        st.markdown("---")
    
    if answered >= 4:
        if st.button("See my career directions →", type="primary", use_container_width=True):
            st.session_state.step = "results"
            st.rerun()
    else:
        st.button("See my career directions →", disabled=True, use_container_width=True)
        st.caption(f"Rate at least 4 skills to continue ({answered}/4)")


def render_career_select():
    st.markdown("""
    <div class="progress-box">
        <div class="progress-steps">
            <span class="done">Entry</span>
            <span class="active">Careers</span>
            <span>Results</span>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:40%"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back"):
            st.session_state.step = "landing"
            st.rerun()
    
    st.markdown("### What are you exploring?")
    st.markdown("Pick 1-3 careers you're curious about")
    
    cols = st.columns(3)
    for i, career in enumerate(CAREERS):
        with cols[i % 3]:
            selected = career["id"] in st.session_state.careers
            card_class = "card-sage" if selected else "card"
            
            st.markdown(f"""
            <div class="{card_class}" style="text-align:center; min-height:140px;">
                <div style="font-size:2rem;">{career['icon']}</div>
                <div style="font-weight:600; color:#1F2421;">{career['title']}</div>
                <div style="font-size:0.85rem; color:#4B5563;">{career['range']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            btn_label = "✓ Selected" if selected else "Select"
            btn_type = "primary" if selected else "secondary"
            if st.button(btn_label, key=f"c_{career['id']}", use_container_width=True, type=btn_type):
                if selected:
                    st.session_state.careers.remove(career["id"])
                elif len(st.session_state.careers) < 3:
                    st.session_state.careers.append(career["id"])
                st.rerun()
    
    st.markdown("")
    if st.session_state.careers:
        if st.button("See my fit for these roles →", type="primary", use_container_width=True):
            st.session_state.step = "results"
            st.rerun()


def render_results():
    st.markdown("""
    <div class="progress-box">
        <div class="progress-steps">
            <span class="done">Entry</span>
            <span class="done">Assessment</span>
            <span class="active">Results</span>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:100%"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    strengths, gaps = get_strengths_and_gaps(st.session_state.skills)
    if not strengths:
        strengths = ["Problem solving", "Communication"]
    if not gaps:
        gaps = ["Data skills"]
    
    readiness, readiness_class = get_readiness(len(gaps))
    
    # Header
    st.markdown("""
    <div style="text-align:center; margin-bottom:2rem;">
        <h2 style="font-family:'Fraunces',serif; font-size:1.75rem; color:#1F2421;">Your CareerCheck Results</h2>
        <p style="color:#4B5563;">Here's what we found based on your inputs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Strengths & Gaps
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Your Strengths**")
        pills = " ".join([f'<span class="pill pill-sage">{s}</span>' for s in strengths])
        st.markdown(pills, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Growth Areas**")
        pills = " ".join([f'<span class="pill pill-stretch">{s}</span>' for s in gaps])
        st.markdown(pills, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Directions
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Your Career Directions**")
    
    st.markdown(f"""
    <div class="dir-card dir-deeper">
        <div class="dir-title">🎯 Go deeper: Product Manager <span class="match-badge match-ready">85% match</span></div>
        <div class="dir-meta">$95k–$180k median salary</div>
    </div>
    <div class="dir-card dir-lateral">
        <div class="dir-title">↔️ Lateral move: Business Analyst <span class="match-badge match-stretch">72% match</span></div>
        <div class="dir-meta">$70k–$130k median salary</div>
    </div>
    <div class="dir-card dir-stretch">
        <div class="dir-title">🚀 Stretch path: Data Scientist <span class="match-badge match-stretch">55% match</span></div>
        <div class="dir-meta">$90k–$165k median salary</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Timeline (dark card)
    st.markdown('<div class="card-dark">', unsafe_allow_html=True)
    st.markdown("<p style='color:#9CA3AF; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:1rem;'>Your Path</p>", unsafe_allow_html=True)
    st.markdown("""
    <div class="timeline">
        <div class="tl-item tl-direction">
            <div class="tl-label">6-12 Month Direction</div>
            <div class="tl-title">Explore Product Manager while maintaining stable income</div>
        </div>
        <div class="tl-item tl-phase">
            <div class="tl-label">3-Month Phase</div>
            <div class="tl-title">Exploration & Foundations</div>
            <div class="tl-body">Test if this direction feels right through conversations and experiments.</div>
        </div>
        <div class="tl-item tl-sprint">
            <div class="tl-label">4-Week Sprint</div>
            <div class="tl-title">Talk to 2 PMs, start 1 project, sample 1 course</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Built-in Coach
    st.markdown('<div class="coach-box">', unsafe_allow_html=True)
    st.markdown('<div class="coach-header">💬 AI Career Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="coach-sub">Get guidance here, or take your results to ChatGPT/Claude below</div>', unsafe_allow_html=True)
    
    user_input = st.text_area(
        "What feels most important, unclear, or scary about your career right now?",
        placeholder="Write a few sentences...",
        key="coach_input",
        label_visibility="collapsed"
    )
    
    if st.button("Ask the Coach →", type="primary"):
        if user_input.strip():
            with st.spinner("Thinking..."):
                context = {
                    "direction": "Product Manager",
                    "strengths": strengths,
                    "gaps": gaps,
                    "readiness": readiness
                }
                response, provider = get_ai_response(user_input, context)
                st.session_state.coach_response = response
                st.session_state.coach_provider = provider
            st.rerun()
    
    # FIXED: Safe access to coach_provider
    if st.session_state.coach_response:
        provider = st.session_state.get("coach_provider", "fallback")
        provider_label = ""
        if provider == "claude":
            provider_label = "🟠 Powered by Claude"
        elif provider == "openai":
            provider_label = "🟢 Powered by ChatGPT"
        
        st.markdown(f'<div class="coach-response">{st.session_state.coach_response}</div>', unsafe_allow_html=True)
        if provider_label:
            st.caption(provider_label)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Continue in ChatGPT/Claude section
    st.markdown("---")
    st.markdown("### 🚀 Continue the conversation")
    st.markdown("Take your CareerCheck results to ChatGPT or Claude for deeper exploration:")
    
    # Generate the prompt
    ai_prompt = generate_ai_prompt(strengths, gaps, "Product Manager")
    
    # Copy box
    st.code(ai_prompt, language=None)
    st.caption("👆 Copy this prompt, then click a button below to open ChatGPT or Claude")
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🟠 Open Claude →", "https://claude.ai/new", use_container_width=True)
    with col2:
        st.link_button("🟢 Open ChatGPT →", "https://chat.openai.com/", use_container_width=True)
    
    # Save session - FIXED: Safe access
    save_session({
        "timestamp": datetime.utcnow().isoformat(),
        "entry_mode": st.session_state.entry_mode,
        "skills": st.session_state.skills,
        "careers": st.session_state.careers,
        "strengths": strengths,
        "gaps": gaps,
        "coach_response": st.session_state.get("coach_response"),
        "coach_provider": st.session_state.get("coach_provider")
    })
    
    st.markdown("---")
    st.markdown("*Take this to a mentor, friend, or counsellor. Ask: What feels true? What's missing?*")
    
    if st.button("Start a new CareerCheck"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# =============================================================================
# MAIN
# =============================================================================

def main():
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:1rem;">
        <div style="width:32px; height:32px; background:#4A6741; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-size:1rem;">✧</div>
        <span style="font-family:'Fraunces',serif; font-size:1.25rem; font-weight:600; color:#1F2421;">CareerCraft</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.step == "landing":
        render_landing()
    elif st.session_state.step == "skills":
        render_skills()
    elif st.session_state.step == "career":
        render_career_select()
    elif st.session_state.step == "results":
        render_results()

if __name__ == "__main__":
    main()
