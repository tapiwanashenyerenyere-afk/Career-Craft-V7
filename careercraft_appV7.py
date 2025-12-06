"""
CareerCraft V7.1 - Streamlit Application

Moat & Design:
- Not "just a form" and not "ask an AI what to do with my life".
- Tool you use BEFORE talking to a mentor/friend/counsellor.
- Direction (6–12 months) → Phase (3 months) → Sprint (4 weeks).
- Quantified: skills, match, salary range, uplift estimate, readiness.
- AI Career Coach as pre-conversation layer (values, constraints, language).
- Local actions: courses, events, communities pulled into the sprint.
- Data collected for learning (JSON files) + simple admin analytics.
"""

import streamlit as st
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# Optional: Anthropic for AI Coach
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="CareerCraft - CareerChecks for clearer decisions",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_DIR = Path("careercraft_data")
DATA_DIR.mkdir(exist_ok=True)

# =============================================================================
# DATA DEFINITIONS
# =============================================================================

SKILL_GROUPS = {
    "cognitive": {
        "name": "Thinking",
        "icon": "🧠",
        "skills": ["Problem Solving", "Systems Thinking", "Critical Analysis", "Research"]
    },
    "technical": {
        "name": "Technical",
        "icon": "⚙️",
        "skills": ["Programming", "Data Analysis", "Design", "Tools"]
    },
    "people": {
        "name": "People",
        "icon": "💬",
        "skills": ["Communication", "Leadership", "Mentoring", "Collaboration"]
    },
    "execution": {
        "name": "Delivery",
        "icon": "🚀",
        "skills": ["Project Management", "Sales", "Operations", "Process Design"]
    }
}

SKILL_LEVELS = [
    {"label": "Never", "value": 10},
    {"label": "Learning", "value": 35},
    {"label": "Sometimes", "value": 60},
    {"label": "Weekly", "value": 90}
]

CAREERS = [
    {"id": "software-dev", "title": "Software Developer", "icon": "💻", "median": 132270, "p10": 79000, "p90": 198000, "growth": 25, "category": "Tech", "skills": ["Programming", "Problem Solving", "Systems Thinking"]},
    {"id": "data-scientist", "title": "Data Scientist", "icon": "📊", "median": 108020, "p10": 63000, "p90": 184000, "growth": 36, "category": "Tech", "skills": ["Data Analysis", "Programming", "Research"]},
    {"id": "product-manager", "title": "Product Manager", "icon": "🎯", "median": 149000, "p10": 95000, "p90": 215000, "growth": 8, "category": "Tech", "skills": ["Communication", "Problem Solving", "Leadership"]},
    {"id": "data-analyst", "title": "Data Analyst", "icon": "📉", "median": 82640, "p10": 50000, "p90": 127000, "growth": 23, "category": "Tech", "skills": ["Data Analysis", "Communication", "Tools"]},
    {"id": "ux-designer", "title": "UX Designer", "icon": "🎨", "median": 97990, "p10": 58000, "p90": 155000, "growth": 16, "category": "Tech", "skills": ["Design", "Research", "Communication"]},
    {"id": "cybersecurity", "title": "Cybersecurity", "icon": "🔐", "median": 120360, "p10": 72000, "p90": 182000, "growth": 33, "category": "Tech", "skills": ["Systems Thinking", "Problem Solving", "Tools"]},
    {"id": "marketing-manager", "title": "Marketing Manager", "icon": "📈", "median": 140040, "p10": 78000, "p90": 208000, "growth": 6, "category": "Business", "skills": ["Communication", "Data Analysis", "Leadership"]},
    {"id": "consultant", "title": "Consultant", "icon": "🎩", "median": 99410, "p10": 57000, "p90": 167000, "growth": 10, "category": "Business", "skills": ["Problem Solving", "Communication", "Critical Analysis"]},
    {"id": "project-manager", "title": "Project Manager", "icon": "📋", "median": 95370, "p10": 57000, "p90": 159000, "growth": 6, "category": "Business", "skills": ["Project Management", "Communication", "Leadership"]},
    {"id": "business-analyst", "title": "Business Analyst", "icon": "💼", "median": 99410, "p10": 57000, "p90": 167000, "growth": 9, "category": "Business", "skills": ["Critical Analysis", "Communication", "Process Design"]},
    {"id": "nurse", "title": "Registered Nurse", "icon": "👩‍⚕️", "median": 86070, "p10": 63000, "p90": 129000, "growth": 6, "category": "Healthcare", "skills": ["Communication", "Problem Solving", "Collaboration"]},
    {"id": "health-admin", "title": "Health Admin", "icon": "🏥", "median": 110680, "p10": 64000, "p90": 209000, "growth": 28, "category": "Healthcare", "skills": ["Leadership", "Operations", "Communication"]},
    {"id": "teacher", "title": "Teacher/Trainer", "icon": "📚", "median": 61690, "p10": 42000, "p90": 99000, "growth": 1, "category": "Education", "skills": ["Communication", "Mentoring", "Research"]},
    {"id": "content-creator", "title": "Content Creator", "icon": "📱", "median": 62500, "p10": 35000, "p90": 120000, "growth": 12, "category": "Creative", "skills": ["Communication", "Design", "Research"]},
]

PHASE_TEMPLATES = {
    "Ready": {
        "name": "Activation & Visibility",
        "goal": "Make your move visible and start building track record in your target role."
    },
    "Stretch": {
        "name": "Exploration & Foundations",
        "goal": "Understand the work, build basic skills, and test if this direction feels right."
    },
    "Long-shot": {
        "name": "Discovery & Skill Building",
        "goal": "Learn what this path requires and start closing your biggest skill gaps."
    }
}

OPPORTUNITIES = {
    "courses": [
        {"id": "course_ga_pm", "title": "Intro to Product Management", "provider": "General Assembly", "duration": "4 weeks", "mode": "Online", "cost": "$650", "tags": ["product-manager", "business-analyst"]},
        {"id": "course_google_da", "title": "Google Data Analytics", "provider": "Coursera", "duration": "6 months", "mode": "Online", "cost": "$39/mo", "tags": ["data-analyst", "data-scientist"]},
        {"id": "course_tafe_analytics", "title": "Data Analytics for Non-Analysts", "provider": "Local TAFE", "duration": "6 weeks", "mode": "Evenings", "cost": "$400", "tags": ["data-analyst", "business-analyst"]},
        {"id": "course_ux_google", "title": "Google UX Design Certificate", "provider": "Coursera", "duration": "6 months", "mode": "Online", "cost": "$39/mo", "tags": ["ux-designer"]},
        {"id": "course_leadership", "title": "Leading People & Teams", "provider": "Michigan", "duration": "5 months", "mode": "Online", "cost": "$49/mo", "tags": ["product-manager", "project-manager", "marketing-manager"]},
    ],
    "events": [
        {"id": "event_pm_meetup", "title": "Product Meetup – PMs in Tech", "provider": "Meetup", "date": "Mar 27", "time": "6:00–8:30pm", "mode": "In person", "tags": ["product-manager"]},
        {"id": "event_data_panel", "title": "Careers in Data & Product", "provider": "Uni Careers", "date": "Next Thursday", "time": "12:00pm", "mode": "Online", "tags": ["data-analyst", "data-scientist", "product-manager"]},
        {"id": "event_ux_workshop", "title": "UX Portfolio Workshop", "provider": "General Assembly", "date": "Feb 20", "time": "6:00pm", "mode": "Hybrid", "tags": ["ux-designer"]},
        {"id": "event_tech_networking", "title": "Tech Networking Night", "provider": "StartupVic", "date": "Mar 15", "time": "5:30pm", "mode": "In person", "tags": ["software-dev", "data-scientist", "product-manager"]},
    ],
    "communities": [
        {"id": "comm_african_tech", "title": "African Tech & Product Melbourne", "provider": "Meetup", "frequency": "Monthly", "mode": "Hybrid", "tags": ["product-manager", "software-dev"]},
        {"id": "comm_early_analytics", "title": "Early Careers in Analytics", "provider": "Discord", "frequency": "Always on", "mode": "Online", "tags": ["data-analyst", "data-scientist"]},
        {"id": "comm_women_tech", "title": "Women in Tech Melbourne", "provider": "Slack", "frequency": "Weekly events", "mode": "Hybrid", "tags": ["software-dev", "ux-designer", "product-manager"]},
        {"id": "comm_pm_circle", "title": "Product Manager Circle", "provider": "LinkedIn", "frequency": "Bi-weekly", "mode": "Online", "tags": ["product-manager"]},
    ]
}

# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    /* Global app background */
    .stApp {
        background-color: #f9fafb;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hero card like ScoreApp / Airwallex */
    .hero-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 2.5rem 2rem;
        box-shadow: 0 32px 80px rgba(15,23,42,0.08);
        border: 1px solid #e5e7eb;
        margin-bottom: 2rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        font-weight: 500;
        color: #4b5563;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        margin-bottom: 0.9rem;
    }
    .hero-title {
        font-size: 2.5rem;
        line-height: 1.1;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.75rem;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #4b5563;
        max-width: 44rem;
        margin-bottom: 1.2rem;
    }
    .hero-subsubtitle {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }
    .hero-meta {
        font-size: 0.8rem;
        color: #9ca3af;
    }

    .card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }

    .card-purple {
        background: linear-gradient(135deg, #f5f3ff, #ede9fe);
        border: 1px solid #c4b5fd;
        padding: 1rem;
        border-radius: 12px;
    }

    .card-blue {
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        border: 1px solid #93c5fd;
        padding: 1rem;
        border-radius: 12px;
    }

    .card-green {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 1px solid #86efac;
        padding: 1rem;
        border-radius: 12px;
    }

    .hero-gradient {
        background: linear-gradient(135deg, #6366f1 0%, #7c3aed 50%, #f97316 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-gradient h1 {
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .chat-assistant {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 85%;
    }

    .chat-user {
        background: linear-gradient(135deg, #6366f1, #7c3aed);
        color: white;
        border-radius: 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 85%;
        margin-left: auto;
        text-align: right;
    }

    .progress-bar {
        height: 8px;
        background: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366f1, #f97316);
        border-radius: 4px;
        transition: width 0.5s;
    }

    .stat-card {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        display: inline-block;
        margin: 0.5rem;
        min-width: 120px;
        border: 1px solid rgba(255,255,255,0.6);
    }

    .stat-value {
        font-size: 1.4rem;
        font-weight: 700;
    }

    .stat-label {
        font-size: 0.8rem;
        opacity: 0.9;
    }

    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .section-label-purple { color: #7c3aed; }
    .section-label-blue { color: #2563eb; }
    .section-label-green { color: #16a34a; }

    /* Stepper */
    .stepper {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.75rem;
        margin: 0.3rem 0 1.1rem 0;
        color: #6b7280;
        flex-wrap: wrap;
    }
    .step-circle {
        width: 22px;
        height: 22px;
        border-radius: 999px;
        border: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        background: #ffffff;
    }
    .step-circle-active {
        border-color: #4f46e5;
        background: #4f46e5;
        color: #ffffff;
    }
    .step-circle-done {
        border-color: #22c55e;
        background: #22c55e;
        color: #ffffff;
    }
    .step-label {
        font-weight: 500;
        color: #374151;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"cc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    defaults = {
        "screen": "landing",
        "lens": None,
        "skills": {},
        "exploring": [],
        "selected_career": None,
        "active_tab": "overview",
        "chat_messages": [],
        "values": {"priorities": [], "constraints": [], "raw_responses": []},
        "coach_summary": {
            "direction_6_12m": "",
            "phase_3m": {"name": "", "goal": ""},
            "sprint_4w": {"title": "", "rationale": "", "actions": []},
            "vision_12m": "",
            "check_in_date": (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")
        },
        "selected_opportunities": [],
        "completed_actions": [],
        "started_at": datetime.now().isoformat(),
        "feedback_rating": None,
        "feedback_comment": ""
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def render_stepper(current_index: int):
    """Simple 4-step visual: Map → Directions → Report → Sprint."""
    steps = ["Map", "Directions", "Report & Coach", "Sprint"]
    html = '<div class="stepper">'
    for i, label in enumerate(steps):
        if i < current_index:
            circle_class = "step-circle step-circle-done"
            icon = "✓"
        elif i == current_index:
            circle_class = "step-circle step-circle-active"
            icon = str(i + 1)
        else:
            circle_class = "step-circle"
            icon = str(i + 1)

        html += f'''
        <div style="display:flex;align-items:center;gap:0.25rem;">
            <div class="{circle_class}">{icon}</div>
            <div class="step-label">{label}</div>
        </div>
        '''
        if i < len(steps) - 1:
            html += '<div style="flex:0 0 16px;height:1px;background:#e5e7eb;margin:0 0.25rem;"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def get_skill(name):
    return st.session_state.skills.get(name, 0)

def get_group_score(group_key):
    group = SKILL_GROUPS[group_key]
    scores = [get_skill(s) for s in group["skills"] if get_skill(s) > 0]
    return round(sum(scores) / len(scores)) if scores else 0

def get_top_skills():
    skills = [(k, v) for k, v in st.session_state.skills.items() if v > 0]
    skills.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in skills[:5]]

def get_career_match(career):
    top = get_top_skills()
    match = sum(1 for s in career["skills"] if s in top or get_skill(s) >= 50)
    return round((match / len(career["skills"])) * 100)

def get_roi(career):
    gaps = [s for s in career["skills"] if get_skill(s) < 60]
    potential = len(gaps) * round((career["p90"] - career["p10"]) * 0.08)
    hours = len(gaps) * 100
    readiness = "Ready" if len(gaps) <= 1 else "Stretch" if len(gaps) <= 2 else "Long-shot"
    return {"gaps": gaps, "potential": potential, "hours": hours, "readiness": readiness}

def get_directions():
    scored = []
    for c in CAREERS:
        match = get_career_match(c)
        gaps = [s for s in c["skills"] if get_skill(s) < 50]
        scored.append({**c, "match": match, "gaps": gaps})
    scored.sort(key=lambda x: x["match"], reverse=True)

    return {
        "deeper": [c for c in scored if c["match"] >= 65][:2],
        "lateral": [c for c in scored if 40 <= c["match"] < 65][:3],
        "stretch": [c for c in scored if c["match"] < 40 and (c["growth"] > 15 or c["median"] > 100000)][:2]
    }

def get_relevant_opportunities(career_id):
    def filter_by_tag(items):
        return [i for i in items if career_id in i.get("tags", [])][:3]

    return {
        "courses": filter_by_tag(OPPORTUNITIES["courses"]),
        "events": filter_by_tag(OPPORTUNITIES["events"]),
        "communities": filter_by_tag(OPPORTUNITIES["communities"])
    }

def generate_coach_summary():
    career = next((c for c in CAREERS if c["id"] == st.session_state.selected_career), None)
    if not career:
        return

    roi = get_roi(career)
    top_skills = get_top_skills()
    phase = PHASE_TEMPLATES.get(roi["readiness"], PHASE_TEMPLATES["Stretch"])

    values = st.session_state.values
    has_stability = "stability" in values["priorities"] or "money" in values["constraints"]

    existing_vision = st.session_state.coach_summary.get("vision_12m", "")
    existing_check_in = st.session_state.coach_summary.get(
        "check_in_date",
        (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")
    )

    st.session_state.coach_summary = {
        "direction_6_12m": f"Explore and move toward {career['title']} while {'maintaining stable income' if has_stability else 'building new skills and visibility'}.",
        "phase_3m": {
            "name": phase["name"],
            "goal": phase["goal"]
        },
        "sprint_4w": {
            "title": f"Talk to 2 {career['title']}s, start 1 mini project, sample 1 course",
            "rationale": (
                f"This sprint tests whether {career['title']} work feels energising using your "
                f"existing {' and '.join(top_skills[:2]) if top_skills else 'core'} skills, and "
                f"whether people in those roles see your background as a good fit."
            ),
            "actions": [
                f"Identify 2–3 {career['title']}s on LinkedIn or in your network",
                "Reach out and book 2 short conversations (15–30 min)",
                f"Start 1 small {roi['gaps'][0] if roi['gaps'] else (top_skills[0] if top_skills else 'skills')}-focused project",
                "Sample 1 course or module (even just the free preview)"
            ]
        },
        "vision_12m": existing_vision,
        "check_in_date": existing_check_in
    }

def extract_values(text):
    lower = text.lower()
    priorities = ["growth", "stability", "impact", "creativity", "flexibility", "money", "people", "learning", "leadership", "community"]
    constraints = ["time", "money", "family", "location", "visa", "experience", "degree", "age"]

    for p in priorities:
        if p in lower and p not in st.session_state.values["priorities"]:
            st.session_state.values["priorities"].append(p)

    for c in constraints:
        if c in lower and c not in st.session_state.values["constraints"]:
            st.session_state.values["constraints"].append(c)

# =============================================================================
# AI COACH
# =============================================================================

def get_ai_response(user_message: str):
    career = next((c for c in CAREERS if c["id"] == st.session_state.selected_career), None)
    roi = get_roi(career) if career else {"gaps": [], "readiness": "Unknown"}
    top_skills = get_top_skills()

    system_prompt = f"""You are a thoughtful career coach. Context: exploring {career['title'] if career else 'careers'}, skills: {', '.join(top_skills)}, gaps: {', '.join(roi['gaps'])}, readiness: {roi['readiness']}.

Help them articulate values, constraints, and what success looks like. Keep responses under 80 words. Ask one follow-up question.

Remember: real career change takes months to years. You are helping them choose better experiments, not promising transformation in weeks."""
    # Anthropic if available
    if ANTHROPIC_AVAILABLE:
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
            if api_key:
                client = Anthropic(api_key=api_key)
                messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages]
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=250,
                    system=system_prompt,
                    messages=messages
                )
                return response.content[0].text
        except Exception:
            pass  # fall back below

    fallbacks = [
        f"That is helpful to hear. It sounds like your goals really matter to you. What would ‘good progress’ look like in 3 months if you were moving toward {career['title'] if career else 'your target path'}?",
        "Thanks for sharing that. Career moves unfold over months, not weeks. What constraints are you working within right now – time, money, location, or something else?",
        "That makes sense. If you could run one small experiment over the next month to test this, what would it look like?"
    ]
    idx = len(st.session_state.chat_messages) % len(fallbacks)
    return fallbacks[idx]

def start_conversation():
    career = next((c for c in CAREERS if c["id"] == st.session_state.selected_career), None)
    if career and not st.session_state.chat_messages:
        st.session_state.chat_messages = [{
            "role": "assistant",
            "content": (
                f"I see you are exploring {career['title']}. I am not here to predict a perfect job, "
                "but to help you describe what matters, what is hard, and what a realistic next experiment looks like. "
                "What matters most in your career right now – growth, stability, impact, or something else?"
            )
        }]

# =============================================================================
# DATA COLLECTION
# =============================================================================

def collect_data():
    career = next((c for c in CAREERS if c["id"] == st.session_state.selected_career), None)
    roi = get_roi(career) if career else None

    return {
        "session_id": st.session_state.session_id,
        "session_type": "first_run",
        "timestamp": datetime.now().isoformat(),
        "started_at": st.session_state.started_at,
        "user_location": {"city": "Melbourne", "country": "AU"},

        "entry_path": st.session_state.lens,
        "skills": st.session_state.skills,
        "skill_count": len([k for k, v in st.session_state.skills.items() if v > 0]),

        "exploring_roles": st.session_state.exploring,
        "selected_career": st.session_state.selected_career,
        "career_title": career["title"] if career else None,

        "results": {
            "match": get_career_match(career) if career else None,
            "potential_uplift": roi["potential"] if roi else None,
            "readiness": roi["readiness"] if roi else None,
            "salary_range": {
                "p10": career["p10"],
                "p50": career["median"],
                "p90": career["p90"]
            } if career else None,
            "gaps": roi["gaps"] if roi else []
        } if career else None,

        "values": st.session_state.values,
        "coach_summary": st.session_state.coach_summary,

        "opportunities": [
            {"id": oid, "selected": True}
            for oid in st.session_state.selected_opportunities
        ],

        "chat_transcript": st.session_state.chat_messages,

        "completed_assessment": len([k for k, v in st.session_state.skills.items() if v > 0]) >= 4,
        "viewed_report": st.session_state.screen in ["report", "wrapup"],
        "had_conversation": len(st.session_state.chat_messages) > 2,
        "set_experiment": bool(st.session_state.coach_summary.get("sprint_4w", {}).get("title")),
        "selected_opportunities_count": len(st.session_state.selected_opportunities),
        "set_long_term_vision": bool(st.session_state.coach_summary.get("vision_12m")),
        "feedback": {
            "rating": st.session_state.get("feedback_rating"),
            "comment": st.session_state.get("feedback_comment", "")
        }
    }

def save_session():
    data = collect_data()
    filepath = DATA_DIR / f"{st.session_state.session_id}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return filepath

# =============================================================================
# SCREENS
# =============================================================================

def render_landing():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-badge">
                🧪 CareerCheck • ~7–10 minutes
            </div>
            <div class="hero-title">
                Build a clearer career story<br/>before you talk to anyone.
            </div>
            <p class="hero-subtitle">
                CareerCraft takes your skills and options and turns them into a 6–12 month direction,
                a 3-month phase, and a 4-week sprint you can take to a mentor, friend, or counsellor.
            </p>
            <p class="hero-subsubtitle">
                Not a magic quiz. Not a chatbot pretending to know your destiny. A structured pre-conversation layer.
            </p>
            <p class="hero-meta">
                🌏 For students, early-career professionals, career-changers, and the mentors who back them.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_main, col_side = st.columns([2.2, 1.4])

    with col_main:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✨ Start a CareerCheck", type="primary", use_container_width=True, key="start_main"):
                st.session_state.lens = "skills"
                st.session_state.screen = "skills"
                st.rerun()
            st.caption("Free. No login. Best used before a real conversation.")
        with c2:
            st.markdown("**You will leave with:**")
            st.markdown("- A 6–12 month *direction*\n- A 3-month *phase focus*\n- A concrete 4-week *experiment*")

    with col_side:
        st.markdown("**How CareerCraft is different**")
        st.markdown(
            "- Direction, not prediction\n"
            "- Designed for repeated use (2–4 checks over months)\n"
            "- Built for conversations: mentor, counsellor, friend"
        )

    st.markdown("---")

    st.markdown("#### Start from what feels easier today")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("###### 🎯 Start from your skills")
        st.markdown(
            "Map how you actually spend your energy each week, across thinking, technical, people, and delivery skills."
        )
        if st.button("Start from my skills →", use_container_width=True, key="btn_skills_card"):
            st.session_state.lens = "skills"
            st.session_state.screen = "skills"
            st.rerun()

    with col2:
        st.markdown("###### 🧭 Start from a career")
        st.markdown(
            "Pick 1–3 roles you are exploring and get a quick read on match, gaps, and what a realistic path might look like."
        )
        if st.button("Start from a career →", use_container_width=True, key="btn_careers_card"):
            st.session_state.lens = "careers"
            st.session_state.screen = "careers"
            st.rerun()

    st.markdown("---")
    cols = st.columns(4)
    with cols[0]:
        st.markdown("📊 **Salary bands & skill gaps**")
    with cols[1]:
        st.markdown(f"🧭 **{len(CAREERS)} example careers**")
    with cols[2]:
        st.markdown("💬 **AI coach (pre-conversation)**")
    with cols[3]:
        st.markdown("🔁 **Repeatable CareerChecks over months**")

def render_skills_entry():
    answered = len([k for k, v in st.session_state.skills.items() if v > 0])
    total = sum(len(g["skills"]) for g in SKILL_GROUPS.values())
    pct = int((answered / total) * 100)

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back"):
            st.session_state.screen = "landing"
            st.rerun()
    with col2:
        render_stepper(0)
        st.markdown(f"**{answered}/{total} skills** mapped")
        st.markdown(
            f'<div class="progress-bar"><div class="progress-fill" style="width: {pct}%;"></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("## Map your skills")
    st.markdown("Think about how you actually spend your time in a typical week.")

    for group_key, group in SKILL_GROUPS.items():
        with st.expander(f"{group['icon']} {group['name']}", expanded=True):
            for skill in group["skills"]:
                cols = st.columns([2, 4])
                with cols[0]:
                    st.markdown(f"**{skill}**")
                with cols[1]:
                    level_cols = st.columns(4)
                    for i, level in enumerate(SKILL_LEVELS):
                        with level_cols[i]:
                            btn_type = "primary" if get_skill(skill) == level["value"] else "secondary"
                            if st.button(
                                level["label"],
                                key=f"skill_{skill}_{level['value']}",
                                type=btn_type,
                                use_container_width=True,
                            ):
                                st.session_state.skills[skill] = level["value"]
                                st.rerun()

    st.markdown("---")

    if answered >= 4:
        if st.button("See my career directions →", type="primary", use_container_width=True):
            st.session_state.screen = "directions"
            st.rerun()
    else:
        st.button("See my career directions →", disabled=True, use_container_width=True)
        st.caption("Map at least 4 skills to continue.")

def render_careers_entry():
    col_top_1, col_top_2 = st.columns([1, 4])
    with col_top_1:
        if st.button("← Back"):
            st.session_state.screen = "landing"
            st.rerun()
    with col_top_2:
        render_stepper(0)

    st.markdown("## What are you exploring?")
    st.markdown("Pick 1–3 careers you are curious about.")

    cols = st.columns(4)
    for i, career in enumerate(CAREERS):
        with cols[i % 4]:
            is_selected = career["id"] in st.session_state.exploring
            btn_style = "primary" if is_selected else "secondary"

            if st.button(
                f"{career['icon']}\n{career['title']}\n${career['median']//1000}k",
                key=f"career_{career['id']}",
                type=btn_style,
                use_container_width=True,
            ):
                if is_selected:
                    st.session_state.exploring.remove(career["id"])
                elif len(st.session_state.exploring) < 3:
                    st.session_state.exploring.append(career["id"])
                st.rerun()

    if st.session_state.exploring:
        st.markdown("---")
        st.markdown("**Quick check:** Which skills feel most like you across these roles?")

        all_skills = set()
        for cid in st.session_state.exploring:
            career = next((c for c in CAREERS if c["id"] == cid), None)
            if career:
                all_skills.update(career["skills"])

        skill_list = list(all_skills)
        cols = st.columns(min(len(skill_list), 4))
        for i, skill in enumerate(skill_list):
            with cols[i % 4]:
                is_active = get_skill(skill) >= 60
                btn_type = "primary" if is_active else "secondary"
                if st.button(skill, key=f"quick_{skill}", type=btn_type, use_container_width=True):
                    st.session_state.skills[skill] = 30 if is_active else 75
                    st.rerun()

    st.markdown("---")

    if st.session_state.exploring:
        if st.button("See my career directions →", type="primary", use_container_width=True):
            st.session_state.screen = "directions"
            st.rerun()
    else:
        st.button("See my career directions →", disabled=True, use_container_width=True)

def render_directions():
    col_top_1, col_top_2 = st.columns([1, 4])
    with col_top_1:
        if st.button("← Edit"):
            st.session_state.screen = "skills" if st.session_state.lens == "skills" else "careers"
            st.rerun()
    with col_top_2:
        render_stepper(1)

    directions = get_directions()
    top_skills = get_top_skills()

    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown("### 🎯 Your skills snapshot")
        for group_key, group in SKILL_GROUPS.items():
            score = get_group_score(group_key)
            st.markdown(f"**{group['icon']} {group['name']}** – {score}%")
            st.progress(score / 100 if score else 0.0)

        if top_skills:
            st.markdown("**Top strengths (from today):**")
            st.markdown(" ".join([f"`{s}`" for s in top_skills]))

    with col2:
        st.markdown("### 🧭 Career directions from here")

        st.markdown("🟢 **Deeper in your lane**")
        if directions["deeper"]:
            for c in directions["deeper"]:
                roi = get_roi(c)
                if st.button(
                    f"{c['icon']} {c['title']} – ${c['p10']//1000}k–${c['p90']//1000}k ({c['match']}% match, {roi['readiness']})",
                    key=f"dir_{c['id']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_career = c["id"]
                    st.session_state.screen = "report"
                    st.rerun()
        else:
            st.caption("Add more skills to see closer matches.")

        st.markdown("🔵 **Lateral moves**")
        if directions["lateral"]:
            for c in directions["lateral"]:
                roi = get_roi(c)
                if st.button(
                    f"{c['icon']} {c['title']} – ${c['p10']//1000}k–${c['p90']//1000}k ({c['match']}% match, {roi['readiness']})",
                    key=f"dir_{c['id']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_career = c["id"]
                    st.session_state.screen = "report"
                    st.rerun()
        else:
            st.caption("Add a few more skills or roles.")

        st.markdown("🟠 **Stretch paths**")
        if directions["stretch"]:
            for c in directions["stretch"]:
                roi = get_roi(c)
                if st.button(
                    f"{c['icon']} {c['title']} – ${c['p10']//1000}k–${c['p90']//1000}k ({c['match']}% match, {roi['readiness']})",
                    key=f"dir_{c['id']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_career = c["id"]
                    st.session_state.screen = "report"
                    st.rerun()
        else:
            st.caption("Your strongest paths are already above.")

def render_report():
    career = next((c for c in CAREERS if c["id"] == st.session_state.selected_career), None)
    if not career:
        st.session_state.screen = "directions"
        st.rerun()
        return

    roi = get_roi(career)
    start_conversation()

    col_top_1, col_top_2 = st.columns([1, 4])
    with col_top_1:
        if st.button("← Back"):
            st.session_state.screen = "directions"
            st.rerun()
    with col_top_2:
        render_stepper(2)

    st.markdown(
        f"""
        <div class="hero-gradient">
            <div style="font-size: 3rem;">{career['icon']}</div>
            <p style="opacity: 0.8;">CareerCheck report for</p>
            <h1>{career['title']}</h1>
            <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
                <div class="stat-card">
                    <div class="stat-value">+${roi['potential']:,}</div>
                    <div class="stat-label">Potential uplift / yr*</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{roi['readiness']}</div>
                    <div class="stat-label">Readiness band</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{roi['hours']}h</div>
                    <div class="stat-label">Approx. hours to close gaps</div>
                </div>
            </div>
            <p style="font-size: 0.8rem; margin-top: 0.75rem; opacity: 0.8;">
                *This is an expectation range, not a guarantee. It should be used as decision support alongside human advice.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📚 Learning", "💬 AI Coach"])

    with tab1:
        st.markdown("### Salary range")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.metric("P10", f"${career['p10']//1000}k")
        with col2:
            st.progress(0.5)
            st.caption(f"Median: ${career['median']//1000}k")
        with col3:
            st.metric("P90", f"${career['p90']//1000}k")

        st.markdown("### Skill gaps to close")
        if roi["gaps"]:
            for gap in roi["gaps"]:
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.markdown(f"**{gap}**")
                with col2:
                    current = get_skill(gap)
                    st.progress(current / 100 if current else 0.0)
                    st.caption(f"{current}% → 70%")
        else:
            st.success("✨ No major gaps – you are effectively ready. Focus on experience and visibility.")

    with tab2:
        if roi["gaps"]:
            for gap in roi["gaps"]:
                st.markdown(f"### {gap}")
                st.markdown("Recommended courses for this skill will appear here as we connect real providers.")
        else:
            st.info("You already have the core skills. The next step is building real projects and social proof.")

    with tab3:
        st.markdown("### 🤖 Career coach (before you talk to a human)")
        st.caption("Use this to get language for your values, constraints, and next experiment.")

        for msg in st.session_state.chat_messages:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="chat-assistant">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)

        user_input = st.text_input("Share what matters to you right now...", key="chat_input")

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Send", type="primary", use_container_width=True):
                if user_input:
                    st.session_state.chat_messages.append({"role": "user", "content": user_input})
                    extract_values(user_input)
                    st.session_state.values["raw_responses"].append(user_input)

                    response = get_ai_response(user_message=user_input)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    generate_coach_summary()
                    save_session()
                    st.rerun()

        st.markdown("**Quick prompts:**")
        prompt_cols = st.columns(4)
        prompts = ["Growth matters most", "I need stability", "Time is limited", "Impact is key"]
        for i, prompt in enumerate(prompts):
            with prompt_cols[i]:
                if st.button(prompt, key=f"prompt_{i}", use_container_width=True):
                    st.session_state.chat_messages.append({"role": "user", "content": prompt})
                    extract_values(prompt)
                    st.session_state.values["raw_responses"].append(prompt)

                    response = get_ai_response(user_message=prompt)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    generate_coach_summary()
                    save_session()
                    st.rerun()

        if st.session_state.values["priorities"]:
            st.markdown("**🎯 What we have heard so far:**")
            st.markdown(" ".join([f"`{p}`" for p in st.session_state.values["priorities"]]))

    st.markdown("---")

    if st.button("Continue to your path & next sprint →", type="primary", use_container_width=True):
        generate_coach_summary()
        st.session_state.screen = "wrapup"
        save_session()
        st.rerun()

def render_wrapup():
    career = next((c for c in CAREERS if c["id"] == st.session_state.selected_career), None)
    if not career:
        st.session_state.screen = "directions"
        st.rerun()
        return

    roi = get_roi(career)
    cs = st.session_state.coach_summary

    if not cs.get("direction_6_12m"):
        generate_coach_summary()
        cs = st.session_state.coach_summary

    col_top_1, col_top_2 = st.columns([1, 4])
    with col_top_1:
        if st.button("← Back"):
            st.session_state.screen = "report"
            st.rerun()
    with col_top_2:
        render_stepper(3)

    st.markdown(
        """
        <div class="card-green" style="padding: 2rem; border-radius: 16px; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <div style="width: 48px; height: 48px; background: #22c55e; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem;">✓</div>
                <div>
                    <h2 style="margin: 0;">CareerCheck #1 complete 🎯</h2>
                    <p style="margin: 0; color: #4b5563;">You now have direction, a phase focus, and a next sprint to take into real conversations.</p>
                </div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; margin-top: 1rem; font-size: 0.875rem;">
                <strong>Careers move over months and years, not weeks.</strong> CareerCraft exists to support 2–4 CareerChecks over time, so each sprint builds on the last.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## 🧭 Your path and next sprint")

    st.markdown('<div class="card-purple"><div class="section-label section-label-purple">6–12 MONTH DIRECTION</div></div>', unsafe_allow_html=True)
    direction = st.text_area(
        "Direction",
        value=cs.get("direction_6_12m", ""),
        key="direction_input",
        label_visibility="collapsed",
        height=68,
    )
    if direction != cs.get("direction_6_12m"):
        st.session_state.coach_summary["direction_6_12m"] = direction

    st.markdown("")

    st.markdown('<div class="card-blue"><div class="section-label section-label-blue">THIS 3-MONTH PHASE</div></div>', unsafe_allow_html=True)
    phase_name = st.text_input(
        "Phase name",
        value=cs.get("phase_3m", {}).get("name", ""),
        key="phase_name_input",
        label_visibility="collapsed",
    )
    phase_goal = st.text_area(
        "Phase goal",
        value=cs.get("phase_3m", {}).get("goal", ""),
        key="phase_goal_input",
        label_visibility="collapsed",
        height=68,
    )

    if phase_name != cs.get("phase_3m", {}).get("name"):
        st.session_state.coach_summary["phase_3m"]["name"] = phase_name
    if phase_goal != cs.get("phase_3m", {}).get("goal"):
        st.session_state.coach_summary["phase_3m"]["goal"] = phase_goal

    st.markdown("")

    st.markdown('<div class="card-green"><div class="section-label section-label-green">NEXT 4-WEEK SPRINT</div></div>', unsafe_allow_html=True)
    sprint_title = st.text_input(
        "Sprint title",
        value=cs.get("sprint_4w", {}).get("title", ""),
        key="sprint_title_input",
        label_visibility="collapsed",
    )

    if sprint_title != cs.get("sprint_4w", {}).get("title"):
        st.session_state.coach_summary["sprint_4w"]["title"] = sprint_title

    st.caption(cs.get("sprint_4w", {}).get("rationale", ""))

    st.markdown("**Actions:**")
    actions = cs.get("sprint_4w", {}).get("actions", [])
    for i, action in enumerate(actions):
        is_completed = i in st.session_state.completed_actions
        if st.checkbox(action, value=is_completed, key=f"action_{i}"):
            if i not in st.session_state.completed_actions:
                st.session_state.completed_actions.append(i)
        else:
            if i in st.session_state.completed_actions:
                st.session_state.completed_actions.remove(i)

    st.markdown("---")
    check_in = st.date_input(
        "Check back in:",
        value=datetime.strptime(
            cs.get("check_in_date", (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")),
            "%Y-%m-%d",
        ),
        key="check_in_date_input",
    )
    st.session_state.coach_summary["check_in_date"] = check_in.strftime("%Y-%m-%d")
    st.caption("Most people get the most out of CareerCraft with 2–4 CareerChecks over a few months.")

    st.markdown("---")
    st.markdown("## 📍 Things you can do in the next 4–6 weeks")
    st.caption("Pick 1–2 that fit your reality. These become part of your sprint.")

    opportunities = get_relevant_opportunities(career["id"])

    st.markdown("### 📚 Courses & learning")
    for opp in opportunities["courses"]:
        is_selected = opp["id"] in st.session_state.selected_opportunities
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{opp['title']}**")
            st.caption(f"{opp['provider']} • {opp['duration']} • {opp['mode']} • {opp['cost']}")
        with col2:
            btn_label = "✓ Added" if is_selected else "+ Add"
            btn_type = "primary" if is_selected else "secondary"
            if st.button(btn_label, key=f"opp_{opp['id']}", type=btn_type):
                if is_selected:
                    st.session_state.selected_opportunities.remove(opp["id"])
                else:
                    st.session_state.selected_opportunities.append(opp["id"])
                st.rerun()
    if not opportunities["courses"]:
        st.caption("No specific courses found for this example path yet.")

    st.markdown("### 🎤 Networking & events")
    for opp in opportunities["events"]:
        is_selected = opp["id"] in st.session_state.selected_opportunities
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{opp['title']}**")
            st.caption(f"{opp['provider']} • {opp['date']} • {opp['mode']}")
        with col2:
            btn_label = "✓ Added" if is_selected else "+ Add"
            btn_type = "primary" if is_selected else "secondary"
            if st.button(btn_label, key=f"opp_{opp['id']}", type=btn_type):
                if is_selected:
                    st.session_state.selected_opportunities.remove(opp["id"])
                else:
                    st.session_state.selected_opportunities.append(opp["id"])
                st.rerun()
    if not opportunities["events"]:
        st.caption("No upcoming events found for this example path yet.")

    st.markdown("### 👥 Communities & groups")
    for opp in opportunities["communities"]:
        is_selected = opp["id"] in st.session_state.selected_opportunities
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{opp['title']}**")
            st.caption(f"{opp['provider']} • {opp['frequency']} • {opp['mode']}")
        with col2:
            btn_label = "✓ Added" if is_selected else "+ Add"
            btn_type = "primary" if is_selected else "secondary"
            if st.button(btn_label, key=f"opp_{opp['id']}", type=btn_type):
                if is_selected:
                    st.session_state.selected_opportunities.remove(opp["id"])
                else:
                    st.session_state.selected_opportunities.append(opp["id"])
                st.rerun()
    if not opportunities["communities"]:
        st.caption("No community groups linked for this example path yet.")

    if st.session_state.selected_opportunities:
        st.success(
            "**✅ Added to your sprint:** "
            + ", ".join(
                [
                    next(
                        (o["title"] for cat in OPPORTUNITIES.values() for o in cat if o["id"] == oid),
                        oid,
                    )
                    for oid in st.session_state.selected_opportunities
                ]
            )
        )

    st.markdown("---")
    st.markdown("## 💬 Quick feedback (helps us improve)")

    st.session_state.feedback_rating = st.slider(
        "How helpful was this CareerCheck today?",
        1,
        5,
        st.session_state.feedback_rating or 4,
    )
    st.session_state.feedback_comment = st.text_input(
        "Anything you would like us to do differently next time?",
        value=st.session_state.feedback_comment,
    )

    st.markdown("---")
    st.markdown("## 🔗 Share this & set your next CareerCheck")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**1. Share with someone you trust**")
        if st.button("📋 Generate shareable summary", use_container_width=True):
            cs = st.session_state.coach_summary
            summary = f"""🧭 My CareerCraft Summary

📍 6–12 MONTH DIRECTION:
{cs.get('direction_6_12m', '')}

📅 THIS 3-MONTH PHASE: {cs.get('phase_3m', {}).get('name', '')}
{cs.get('phase_3m', {}).get('goal', '')}

🏃 NEXT 4-WEEK SPRINT:
{cs.get('sprint_4w', {}).get('title', '')}

Actions:
{chr(10).join(['• ' + a for a in cs.get('sprint_4w', {}).get('actions', [])])}

📆 Next CareerCheck: {cs.get('check_in_date', '')}

Questions for us to talk about:
• What do you see in me that this report missed?
• Does this direction feel realistic from your perspective?
• If we had to design one experiment for the next month, what would it be?
"""
            st.code(summary, language=None)
            st.info("Copy the text above into an email or message to a mentor, friend, or counsellor.")

    with col2:
        st.markdown("**2. Drop this into your calendar**")
        check_in_str = cs.get("check_in_date", "")
        ics_snippet = f"""Title: CareerCraft Check-in
Date: {check_in_str}
Description:
Review this CareerCheck, update skills, and decide on your next sprint.
Bring your notes from any conversations you had about this plan.
"""
        st.code(ics_snippet, language=None)
        st.caption("Copy this text into a new event in Google Calendar / Outlook on your check-in date.")

        if st.button("✅ Confirm & save session", type="primary", use_container_width=True):
            save_session()
            st.success("Session saved. When you return, we will pick up from what you actually did, not just what you planned.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        data = collect_data()
        st.download_button(
            "📥 Export session JSON",
            json.dumps(data, indent=2),
            f"careercraft_{st.session_state.session_id}.json",
            "application/json",
        )
    with col2:
        st.caption("Next version will let you log in and see all your past CareerChecks in one place.")

# =============================================================================
# ADMIN PANEL
# =============================================================================

def render_admin():
    st.markdown("# 📊 Admin analytics")

    sessions = []
    for f in DATA_DIR.glob("*.json"):
        try:
            with open(f) as file:
                sessions.append(json.load(file))
        except Exception:
            pass

    if not sessions:
        st.warning("No sessions collected yet.")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total sessions", len(sessions))
    with col2:
        completed = sum(1 for s in sessions if s.get("completed_assessment"))
        st.metric("Completed assessment", completed)
    with col3:
        had_chat = sum(1 for s in sessions if s.get("had_conversation"))
        st.metric("Had AI conversation", had_chat)
    with col4:
        set_exp = sum(1 for s in sessions if s.get("set_experiment"))
        st.metric("Set experiment", set_exp)

    st.markdown("---")

    st.markdown("### Popular careers")
    careers_explored = {}
    for s in sessions:
        if s.get("career_title"):
            careers_explored[s["career_title"]] = careers_explored.get(s["career_title"], 0) + 1

    if careers_explored:
        df = pd.DataFrame(list(careers_explored.items()), columns=["Career", "Count"])
        st.bar_chart(df.set_index("Career"))

    st.markdown("### Values mentioned")
    all_values = {}
    for s in sessions:
        for v in s.get("values", {}).get("priorities", []):
            all_values[v] = all_values.get(v, 0) + 1

    if all_values:
        df = pd.DataFrame(list(all_values.items()), columns=["Value", "Count"])
        st.bar_chart(df.set_index("Value"))

    st.markdown("---")
    df_all = pd.DataFrame(sessions)
    csv = df_all.to_csv(index=False)
    st.download_button(
        "📥 Export all sessions (CSV)",
        csv,
        "careercraft_all_sessions.csv",
        "text/csv",
    )

# =============================================================================
# MAIN ROUTER
# =============================================================================

def main():
    # Admin mode via query parameter: ?admin=true
    admin_flag = False
    try:
        qp = st.experimental_get_query_params()
        raw = qp.get("admin")
        if raw:
            admin_flag = any(str(v).lower() == "true" for v in raw)
    except Exception:
        admin_flag = False

    if admin_flag:
        render_admin()
        return

    screen = st.session_state.screen

    if screen == "landing":
        render_landing()
    elif screen == "skills":
        render_skills_entry()
    elif screen == "careers":
        render_careers_entry()
    elif screen == "directions":
        render_directions()
    elif screen == "report":
        render_report()
    elif screen == "wrapup":
        render_wrapup()
    else:
        st.session_state.screen = "landing"
        render_landing()

if __name__ == "__main__":
    main()
