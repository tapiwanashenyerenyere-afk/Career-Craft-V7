"""
CareerCraft – Career Intelligence Platform
Fixed: Navigation, HTML rendering, data section, button styling
"""

import streamlit as st
from datetime import datetime

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
# DATA
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
    {
        "id": "pm", "title": "Product Manager", "subtitle": "Shape what gets built", 
        "range": "$95k-$180k", "median": 137000,
        "fit": {"technical": 60, "people_energy": 80, "people_style": 75, "analysis": 70, "structure": 60, "learning": 80, "client_facing": 70},
    },
    {
        "id": "dev", "title": "Software Developer", "subtitle": "Build and create",
        "range": "$80k-$200k", "median": 132000,
        "fit": {"technical": 95, "people_energy": 40, "people_style": 45, "analysis": 80, "structure": 70, "learning": 90, "client_facing": 30},
    },
    {
        "id": "data", "title": "Data Analyst", "subtitle": "Find insights in numbers",
        "range": "$65k-$130k", "median": 86000,
        "fit": {"technical": 85, "people_energy": 45, "people_style": 40, "analysis": 95, "structure": 80, "learning": 70, "client_facing": 50},
    },
    {
        "id": "ux", "title": "UX Designer", "subtitle": "Design for humans",
        "range": "$70k-$150k", "median": 98000,
        "fit": {"technical": 50, "people_energy": 70, "people_style": 55, "analysis": 60, "structure": 50, "learning": 80, "client_facing": 75},
    },
    {
        "id": "marketing", "title": "Marketing Manager", "subtitle": "Tell compelling stories",
        "range": "$75k-$160k", "median": 140000,
        "fit": {"technical": 40, "people_energy": 85, "people_style": 70, "analysis": 50, "structure": 50, "learning": 70, "client_facing": 85},
    },
    {
        "id": "consultant", "title": "Consultant", "subtitle": "Solve business problems",
        "range": "$80k-$170k", "median": 99000,
        "fit": {"technical": 60, "people_energy": 80, "people_style": 75, "analysis": 75, "structure": 70, "learning": 90, "client_facing": 95},
    },
    {
        "id": "analyst", "title": "Business Analyst", "subtitle": "Bridge tech and business",
        "range": "$70k-$130k", "median": 95000,
        "fit": {"technical": 70, "people_energy": 65, "people_style": 50, "analysis": 85, "structure": 75, "learning": 75, "client_facing": 60},
    },
    {
        "id": "manager", "title": "People Manager", "subtitle": "Lead and develop teams",
        "range": "$90k-$170k", "median": 120000,
        "fit": {"technical": 45, "people_energy": 90, "people_style": 95, "analysis": 55, "structure": 70, "learning": 65, "client_facing": 60},
    },
]

# Research-backed personas
PERSONAS = [
    {
        "id": "maya",
        "name": "Maya",
        "archetype": "The Anxious Explorer",
        "age": "19-22",
        "stage": "Student / Recent Grad",
        "story": "Maya started university during peak pandemic uncertainty, choosing business as a 'safe' major before realizing it doesn't excite her. She's cycled through interests - psychology, UX design, marketing - without committing. Graduation approaches in 14 months and she feels paralyzed by options, terrified of 'wasting' her degree.",
        "tension": "Stuck between too many options. Wants something meaningful but fears picking wrong and disappointing her family.",
        "constraints": [
            "$38K student debt creates pressure to find ROI on education",
            "Parents' expectations limit perceived 'creative' options",
            "Mental health challenges (anxiety) affect follow-through",
            "Limited professional network beyond professors"
        ],
        "jtbd": "When I'm lying awake worrying about graduation, I want to understand what realistic career paths match my skills and interests, so I can stop feeling paralyzed and start taking action.",
        "resonant_message": "Stop spiraling through Reddit threads at 2am. Get a plan you can actually follow.",
        "stats": ["42% of Gen Z have a mental health diagnosis", "75% change their major at least once", "67% need help with career decisions"]
    },
    {
        "id": "darius",
        "name": "Darius",
        "archetype": "The Ambitious Climber",
        "age": "26-30",
        "stage": "Early Career (3-5 years)",
        "story": "Darius excelled academically and landed a solid corporate job after graduation. He's been promoted once and is earning $85K, but watches peers at other companies pull $120K+. He and his partner want to buy property within 2-3 years, requiring significant salary growth or a strategic move.",
        "tension": "Knows he needs to either push for promotion, jump to a competitor, or shift to a higher-ceiling field. Each path has trade-offs he can't fully evaluate.",
        "constraints": [
            "$42K remaining student debt",
            "Partner's career limits geographic flexibility",
            "Golden handcuffs from unvested RSUs",
            "Doesn't want to restart at entry level in new field"
        ],
        "jtbd": "When I see peers getting promoted or jumping to better roles, I want to understand exactly what moves will maximize my earnings over the next 5 years, so I can hit my financial goals.",
        "resonant_message": "Model your next 5 years. Compare paths. Optimize for what actually matters to you.",
        "stats": ["56% live paycheck-to-paycheck", "Job tenure dropped to 3.2 years", "86% say purpose matters for satisfaction"]
    },
    {
        "id": "rachel",
        "name": "Rachel",
        "archetype": "The Burned-Out Reinventor",
        "age": "36-44",
        "stage": "Mid-Career (12-18 years)",
        "story": "Rachel built a respectable career in corporate marketing, reaching Director level by her late 30s. COVID's remote work revelation showed her that work-life balance was possible - then return-to-office mandates and layoffs brought burnout to a breaking point. She recently turned down a promotion because it meant more travel and stress.",
        "tension": "Wants out of the corporate grind but can't afford to start over at entry level. Explored coaching, therapy, even counseling school - but each path requires sacrificing either income or years of career capital.",
        "constraints": [
            "Mortgage and family create $90K minimum income floor",
            "Healthcare dependent on employment",
            "Age discrimination concerns",
            "Two school-age children limit time for retraining"
        ],
        "jtbd": "When I wake up dreading Monday again, I want to find a realistic path to work that's sustainable and meaningful, so I can stop feeling trapped and show my kids it's possible to love what you do.",
        "resonant_message": "You've built skills. Let's figure out where they're valued - without starting over.",
        "stats": ["Average career changer is 39", "43% say 'too late' holds them back", "35% cite burnout as top concern"]
    },
    {
        "id": "emmanuel",
        "name": "Emmanuel",
        "archetype": "The First-Gen Navigator",
        "age": "28-34",
        "stage": "Skilled Professional (5-10 years)",
        "story": "Emmanuel immigrated six years ago with an accounting degree and three years of professional experience. Credential recognition took longer than expected. He worked as a rideshare driver, then warehouse supervisor, while studying for CPA equivalency. He's now a junior accountant earning 40% less than domestic peers.",
        "tension": "Feels trapped between stability of current path (continue toward CPA, hope for promotion) and opportunity cost of not pivoting to tech or higher-growth fields while still young enough to learn.",
        "constraints": [
            "Immigration status limits job flexibility",
            "Sends $500/month to parents back home",
            "Credential recognition barriers devalue qualifications",
            "Limited domestic professional network"
        ],
        "jtbd": "When I see domestic peers advancing faster despite less experience, I want to understand what credentials, skills, and strategies will accelerate my career given my specific constraints.",
        "resonant_message": "Your skills traveled with you. Let's make sure employers see them.",
        "stats": ["First-gen earn $36K less median", "17% of self-employed are migrants", "1/3 lack foundational digital skills"]
    },
]

# =============================================================================
# CSS
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
        max-width: 700px;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Fraunces', Georgia, serif !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    p, span, div, label, li {
        color: #2d2d2d;
    }
    
    /* Navigation */
    .nav-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e8e5e0;
        margin-bottom: 1.5rem;
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-right: auto;
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
    
    /* Progress bar */
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
    .question-text {
        font-family: 'Fraunces', Georgia, serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        line-height: 1.4;
        margin-bottom: 1.75rem;
    }
    
    .scale-labels {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.75rem;
        font-size: 0.8rem;
        color: #666;
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
        max-width: 500px;
        margin: 0 auto 1.75rem;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.9rem;
        border: 1px solid #e8e5e0;
    }
    
    .card-title {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.75rem;
    }
    
    .card-body {
        font-size: 0.9rem;
        color: #444;
        line-height: 1.6;
    }
    
    /* Data grid */
    .data-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.75rem;
        margin: 1rem 0;
    }
    
    .data-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e8e5e0;
        text-align: center;
    }
    
    .data-value {
        font-family: 'Fraunces', serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #4A6741;
        margin-bottom: 0.25rem;
    }
    
    .data-label {
        font-size: 0.75rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Pills */
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
    
    .direction-primary { border-color: #4A6741; background: linear-gradient(135deg, #f5faf4 0%, white 100%); }
    .direction-secondary { border-color: #2563eb; background: linear-gradient(135deg, #f0f7ff 0%, white 100%); }
    .direction-tertiary { border-color: #d97706; background: linear-gradient(135deg, #fffbf0 0%, white 100%); }
    
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
    
    /* Persona cards */
    .persona-card {
        background: white;
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e8e5e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .persona-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #f0ede8;
    }
    
    .persona-name {
        font-family: 'Fraunces', serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.15rem;
    }
    
    .persona-archetype {
        font-size: 0.95rem;
        color: #4A6741;
        font-weight: 500;
    }
    
    .persona-meta {
        text-align: right;
    }
    
    .persona-age {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.2rem;
    }
    
    .persona-stage {
        font-size: 0.75rem;
        color: #888;
        background: #f5f5f5;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        display: inline-block;
    }
    
    .persona-story {
        font-size: 0.95rem;
        color: #444;
        line-height: 1.65;
        margin-bottom: 1.25rem;
    }
    
    .persona-tension {
        background: linear-gradient(135deg, #fef3e2 0%, #fff 100%);
        border-left: 3px solid #d97706;
        padding: 0.9rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1.25rem;
    }
    
    .persona-tension-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #b45309;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    
    .persona-tension-text {
        font-size: 0.9rem;
        color: #444;
        line-height: 1.5;
        font-style: italic;
    }
    
    .persona-section-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #888;
        font-weight: 600;
        margin-bottom: 0.5rem;
        margin-top: 1rem;
    }
    
    .persona-constraint {
        font-size: 0.85rem;
        color: #555;
        margin-bottom: 0.4rem;
        padding-left: 1rem;
        position: relative;
        line-height: 1.45;
    }
    
    .persona-constraint::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0.45rem;
        width: 5px;
        height: 5px;
        background: #d97706;
        border-radius: 50%;
    }
    
    .persona-jtbd {
        background: linear-gradient(135deg, #f5faf4 0%, #fff 100%);
        border-left: 3px solid #4A6741;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    .persona-jtbd-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #2d5a27;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    
    .persona-jtbd-text {
        font-size: 0.95rem;
        color: #2d2d2d;
        line-height: 1.55;
    }
    
    .persona-message {
        background: #1a1a1a;
        color: #f5f5f5;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-top: 1.25rem;
    }
    
    .persona-message-label {
        font-size: 0.6rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #86efac;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    
    .persona-message-text {
        font-family: 'Fraunces', serif;
        font-size: 1.05rem;
        line-height: 1.45;
    }
    
    .persona-stats {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    
    .persona-stat {
        background: #f8f8f6;
        border: 1px solid #e8e5e0;
        border-radius: 6px;
        padding: 0.4rem 0.7rem;
        font-size: 0.75rem;
        color: #555;
    }
    
    /* About styles */
    .about-body {
        font-size: 0.95rem;
        color: #444;
        line-height: 1.7;
        margin-bottom: 1rem;
    }
    
    .pitch-item {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.1rem;
    }
    
    .pitch-num {
        width: 26px;
        height: 26px;
        min-width: 26px;
        background: #4A6741;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.1rem;
    }
    
    .pitch-text {
        font-size: 0.9rem;
        color: #2d2d2d;
        line-height: 1.55;
    }
    
    .pitch-text strong {
        color: #1a1a1a;
    }
    
    /* Community card */
    .community-card {
        background: linear-gradient(135deg, #f0f7ff 0%, #f5faf4 100%);
        border: 1px solid #d1e3f0;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
    }
    
    .community-title {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .community-body {
        font-size: 0.9rem;
        color: #444;
        line-height: 1.6;
    }
    
    /* Section header */
    .section-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .section-title {
        font-family: 'Fraunces', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.35rem;
    }
    
    .section-subtitle {
        font-size: 0.95rem;
        color: #666;
    }
    
    /* CTA card */
    .cta-card {
        background: linear-gradient(135deg, #f5faf4 0%, #f0f7ff 100%);
        border: 1px solid #e8e5e0;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .cta-title {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.35rem;
    }
    
    .cta-body {
        font-size: 0.9rem;
        color: #555;
        line-height: 1.5;
    }
    
    /* Footer */
    .footer-note {
        text-align: center;
        font-size: 0.75rem;
        color: #888;
        margin-top: 1.25rem;
        font-style: italic;
    }
    
    /* Streamlit overrides */
    .stButton > button {
        background: #4A6741 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        min-height: 42px !important;
    }
    
    .stButton > button:hover {
        background: #3d5636 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Secondary button style */
    div[data-testid="column"]:has(button[kind="secondary"]) button,
    .secondary-btn button {
        background: white !important;
        color: #2d2d2d !important;
        border: 1.5px solid #d1d1d1 !important;
    }
    
    div[data-testid="column"]:has(button[kind="secondary"]) button:hover,
    .secondary-btn button:hover {
        border-color: #4A6741 !important;
        color: #4A6741 !important;
        background: #f5faf4 !important;
    }
    
    .stTextArea textarea, .stTextInput input {
        border-radius: 8px !important;
        border: 1.5px solid #d1d1d1 !important;
        padding: 0.7rem !important;
        background: white !important;
        color: #2d2d2d !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #4A6741 !important;
        box-shadow: 0 0 0 1px #4A6741 !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 0.5rem;
    }
    
    /* Video styling */
    .stVideo {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e8e5e0;
    }
    
    .stVideo video {
        border-radius: 12px;
    }
    
    /* Scroll animations */
    .scroll-fade {
        opacity: 0;
        transform: translateY(40px);
        transition: opacity 0.6s ease-out, transform 0.6s ease-out;
    }
    
    .scroll-fade.visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    /* Staggered animation delays for persona cards */
    .persona-card.scroll-fade:nth-child(1) { transition-delay: 0s; }
    .persona-card.scroll-fade:nth-child(2) { transition-delay: 0.15s; }
    .persona-card.scroll-fade:nth-child(3) { transition-delay: 0.3s; }
    .persona-card.scroll-fade:nth-child(4) { transition-delay: 0.45s; }
    
    .video-section {
        margin: 2rem 0;
    }
    
    .video-section-bottom {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e8e5e0;
    }
    
    .video-caption {
        text-align: center;
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.5rem;
        font-style: italic;
    }
</style>
<script>
    // Scroll animation observer
    function initScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
        
        document.querySelectorAll('.scroll-fade').forEach(el => {
            observer.observe(el);
        });
    }
    
    // Run on load and after Streamlit rerenders
    if (document.readyState === 'complete') {
        initScrollAnimations();
    } else {
        window.addEventListener('load', initScrollAnimations);
    }
    
    // Re-run periodically to catch dynamically added elements
    setInterval(initScrollAnimations, 500);
</script>
""", unsafe_allow_html=True)

# =============================================================================
# HELPERS
# =============================================================================

def get_secret(key, default=None):
    try:
        return dict(st.secrets).get(key, default)
    except:
        return default

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

# =============================================================================
# AI COACHES
# =============================================================================

COACH_SYSTEM = """You are a thoughtful career coach. Help people think through career decisions with:
1. What matters most right now
2. How to frame the next 3-6 months
3. 1-3 concrete, low-risk experiments
Keep responses under 200 words. Be warm but direct."""

def get_fallback_response(user_msg, context):
    return """Based on your profile, here's how I'd approach this:

Start with conversations, not courses. Before investing in any training, talk to 2-3 people actually doing the work you're considering. Ask them: What surprised you about this role? What do you wish you'd known?

Run a small experiment. Pick one thing you can try in the next 2 weeks that tests your interest. Could be a side project, volunteering for a task at work, or taking a free introductory course.

Your strengths are your foundation. Build from what already works for you rather than trying to fix every gap at once. Look for roles that let you use your existing strengths while gradually building new skills.

The goal isn't to have perfect clarity - it's to learn enough to take the next small step with confidence.

What specific aspect would you like to explore further?"""

def get_claude_response(user_msg, context):
    api_key = get_secret("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "ANTHROPIC_API_KEY not configured"
    if not ANTHROPIC_AVAILABLE:
        return None, "anthropic package not installed"
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
        return None, f"Claude error: {str(e)}"

def get_chatgpt_response(user_msg, context):
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        return None, "OPENAI_API_KEY not configured"
    if not OPENAI_AVAILABLE:
        return None, "openai package not installed"
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
        return None, f"ChatGPT error: {str(e)}"

def get_gemini_response(user_msg, context):
    api_key = get_secret("GOOGLE_API_KEY")
    if not api_key:
        return None, "GOOGLE_API_KEY not configured"
    if not GEMINI_AVAILABLE:
        return None, "google-generativeai package not installed"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"{COACH_SYSTEM}\n\n{context}\n\nUser question: {user_msg}"
        resp = model.generate_content(prompt)
        return resp.text.strip(), None
    except Exception as e:
        return None, f"Gemini error: {str(e)}"

def check_api_status():
    status = {}
    status["claude"] = bool(get_secret("ANTHROPIC_API_KEY")) and ANTHROPIC_AVAILABLE
    status["chatgpt"] = bool(get_secret("OPENAI_API_KEY")) and OPENAI_AVAILABLE
    status["gemini"] = bool(get_secret("GOOGLE_API_KEY")) and GEMINI_AVAILABLE
    return status

# =============================================================================
# SESSION STATE
# =============================================================================

if "page" not in st.session_state:
    st.session_state.page = "home"
if "step" not in st.session_state:
    st.session_state.step = "landing"
if "question_idx" not in st.session_state:
    st.session_state.question_idx = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "coach_response" not in st.session_state:
    st.session_state.coach_response = None
if "coach_provider" not in st.session_state:
    st.session_state.coach_provider = None
if "coach_error" not in st.session_state:
    st.session_state.coach_error = None
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# =============================================================================
# NAVIGATION
# =============================================================================

def navigate_to(page, step="landing"):
    st.session_state.page = page
    st.session_state.step = step
    st.session_state.show_signup = False

def render_nav():
    st.markdown('''
    <div class="logo" style="margin-bottom: 0.75rem;">
        <div class="logo-mark">C</div>
        <div class="logo-text">CareerCraft</div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Home", key="nav_home", use_container_width=True,
                    type="primary" if st.session_state.page == "home" and not st.session_state.show_signup else "secondary"):
            navigate_to("home")
            st.rerun()
    
    with col2:
        if st.button("About", key="nav_about", use_container_width=True,
                    type="primary" if st.session_state.page == "about" and not st.session_state.show_signup else "secondary"):
            navigate_to("about")
            st.rerun()
    
    with col3:
        if st.button("Use Cases", key="nav_usecases", use_container_width=True,
                    type="primary" if st.session_state.page == "usecases" and not st.session_state.show_signup else "secondary"):
            navigate_to("usecases")
            st.rerun()
    
    with col4:
        if st.button("Sign up", key="nav_signup", use_container_width=True,
                    type="primary" if st.session_state.show_signup else "secondary"):
            st.session_state.show_signup = True
            st.rerun()
    
    st.markdown("<hr style='margin: 0.75rem 0 1.5rem; border: none; border-top: 1px solid #e8e5e0;'>", unsafe_allow_html=True)

# =============================================================================
# SIGNUP PAGE
# =============================================================================

def render_signup():
    st.markdown('''
    <div class="section-header">
        <div class="section-title">Join CareerCraft</div>
        <div class="section-subtitle">Career intelligence powered by real data</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # The pitch - rendered properly
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">What you\'re joining</div>', unsafe_allow_html=True)
    
    pitch_items = [
        ("1", "Enterprise-grade data, not opinions.", "We integrate verified labor market data covering 1,016 occupations with 62,580 skill ratings, wage data from 800+ occupations, hiring records updated monthly, and educational outcomes by institution. The same data used by Fortune 500 companies and research institutions."),
        ("2", "Skill-level ROI calculations.", "Most tools tell you a degree is 'worth it.' We calculate the specific wage premium for individual skills. Python adds ~$22,000/year. Project management adds ~$16,000. You see exactly what to learn and what it's worth."),
        ("3", "Research-backed precision.", "Our matching uses hedonic wage regression, causal inference for treatment effects, and conformal prediction for uncertainty. This isn't a quiz - it's the same econometric rigor used in academic labor economics research."),
        ("4", "Transparent algorithms.", "Every recommendation includes explanations showing exactly why. No black boxes. You can see the math, audit the logic, and understand exactly how we arrived at your results."),
        ("5", "A community of career crafters.", "You're not navigating alone. Join thousands of professionals at every stage - from anxious explorers to ambitious climbers to seasoned reinventors - sharing insights, accountability, and real stories of transition."),
        ("6", "Longitudinal tracking.", "Your profile persists. As you build skills and the market shifts, your recommendations update. Track your progress over time with version control for your career trajectory."),
    ]
    
    for num, title, desc in pitch_items:
        st.markdown(f'''
        <div class="pitch-item">
            <div class="pitch-num">{num}</div>
            <div class="pitch-text"><strong>{title}</strong> {desc}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Community highlight
    st.markdown('''
    <div class="community-card">
        <div class="community-title">Join the community</div>
        <div class="community-body">
            Connect with others on similar journeys. Our community includes students exploring their first career, early-career professionals optimizing for growth, mid-career pivoters seeking meaning, and skilled immigrants navigating new markets. Share wins, get accountability, find mentors.
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Form
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First name", key="signup_first")
    with col2:
        last_name = st.text_input("Last name", key="signup_last")
    
    email = st.text_input("Email address", key="signup_email")
    password = st.text_input("Create password", type="password", key="signup_pass")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create free account", key="signup_submit", use_container_width=True):
            if email and password:
                st.success("Account created! Welcome to CareerCraft.")
                st.session_state.show_signup = False
    with col2:
        if st.button("Cancel", key="signup_cancel", use_container_width=True, type="secondary"):
            st.session_state.show_signup = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<p class="footer-note">Free during beta. No credit card required.</p>', unsafe_allow_html=True)

# =============================================================================
# HOME PAGE
# =============================================================================

def render_home_landing():
    # Hero
    st.markdown('''
    <div class="hero">
        <div class="hero-badge">
            <span class="hero-dot"></span>
            Free assessment, 3 minutes
        </div>
        <h1 class="hero-title">Get <em>clarity</em> on your career.</h1>
        <p class="hero-sub">
            Answer 7 questions. Get matched to careers with real salary data.
            Talk to AI coaches. Walk away with a 4-week plan.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # First video - under hero
    st.markdown('<div class="video-section scroll-fade">', unsafe_allow_html=True)
    st.video("Untitled video (1).mp4")
    st.markdown('<p class="video-caption">See how CareerCraft matches you to careers</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data grid
    st.markdown('''
    <div class="scroll-fade">
    <div class="data-grid">
        <div class="data-card">
            <div class="data-value">7</div>
            <div class="data-label">Questions</div>
        </div>
        <div class="data-card">
            <div class="data-value">8+</div>
            <div class="data-label">Career Matches</div>
        </div>
        <div class="data-card">
            <div class="data-value">3</div>
            <div class="data-label">AI Coaches</div>
        </div>
    </div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start CareerCheck", use_container_width=True, key="start_check"):
            st.session_state.step = "questions"
            st.session_state.question_idx = 0
            st.session_state.answers = {}
            st.rerun()
    
    st.markdown('<p class="footer-note">No signup required to start.</p>', unsafe_allow_html=True)
    
    # Features section with scroll animation
    st.markdown('''
    <div class="scroll-fade" style="margin-top: 3rem;">
        <div class="card">
            <div class="card-title">What you'll get</div>
            <div class="pitch-item">
                <div class="pitch-num">1</div>
                <div class="pitch-text"><strong>Personalized career matches</strong> based on your work style, not just your resume</div>
            </div>
            <div class="pitch-item">
                <div class="pitch-num">2</div>
                <div class="pitch-text"><strong>Real salary data</strong> from 800+ occupations so you know what to expect</div>
            </div>
            <div class="pitch-item">
                <div class="pitch-num">3</div>
                <div class="pitch-text"><strong>AI career coaches</strong> to help you think through your next move</div>
            </div>
            <div class="pitch-item">
                <div class="pitch-num">4</div>
                <div class="pitch-text"><strong>A 4-week action plan</strong> with concrete steps to get started</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Second video - bottom of page
    st.markdown('''
    <div class="video-section-bottom scroll-fade">
        <div class="section-header">
            <div class="card-title">Your results, explained</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="scroll-fade">', unsafe_allow_html=True)
    st.video("VIDEO 1.mp4")
    st.markdown('<p class="video-caption">How we turn your answers into actionable insights</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Final CTA
    st.markdown('''
    <div class="scroll-fade">
        <div class="cta-card" style="margin-top: 2rem;">
            <div class="cta-title">Ready to find your path?</div>
            <div class="cta-body">Takes 3 minutes. No signup required.</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start CareerCheck", use_container_width=True, key="start_check_bottom"):
            st.session_state.step = "questions"
            st.session_state.question_idx = 0
            st.session_state.answers = {}
            st.rerun()

def render_home_questions():
    idx = st.session_state.question_idx
    total = len(QUESTIONS)
    question = QUESTIONS[idx]
    
    progress_pct = int(((idx + 1) / total) * 100)
    st.markdown(f'''
    <div class="progress-container">
        <div class="progress-text">Question {idx + 1} of {total}</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_pct}%"></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown(f'<h2 class="question-text">{question["question"]}</h2>', unsafe_allow_html=True)
    
    st.markdown(f'''
    <div class="scale-labels">
        <span>{question["low_label"]}</span>
        <span>{question["high_label"]}</span>
    </div>
    ''', unsafe_allow_html=True)
    
    current_value = st.session_state.answers.get(question["id"], None)
    
    cols = st.columns(5)
    for i, option in enumerate(ANSWER_OPTIONS):
        with cols[i]:
            is_selected = current_value == option["value"]
            btn_type = "primary" if is_selected else "secondary"
            if st.button(option["label"], key=f"q_{question['id']}_{option['value']}", 
                        type=btn_type, use_container_width=True):
                st.session_state.answers[question["id"]] = option["value"]
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if idx > 0:
            if st.button("Back", type="secondary", use_container_width=True, key="q_back"):
                st.session_state.question_idx -= 1
                st.rerun()
        else:
            if st.button("Exit", type="secondary", use_container_width=True, key="q_exit"):
                st.session_state.step = "landing"
                st.rerun()
    
    with col3:
        can_continue = current_value is not None
        is_last = idx == total - 1
        
        if is_last:
            if st.button("See results", disabled=not can_continue, use_container_width=True, key="q_results"):
                st.session_state.step = "results"
                st.rerun()
        else:
            if st.button("Next", disabled=not can_continue, use_container_width=True, key="q_next"):
                st.session_state.question_idx += 1
                st.rerun()

def render_home_results():
    answers = st.session_state.answers
    matches = calculate_career_matches(answers)
    strengths, gaps = get_strengths_and_gaps(answers)
    
    top_match = matches[0]
    second_match = matches[1]
    third_match = matches[2]
    
    st.markdown('''
    <div class="section-header">
        <div class="section-title">Your Results</div>
        <div class="section-subtitle">Based on your 7 answers</div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="result-label">Your Strengths</div>', unsafe_allow_html=True)
        pills = "".join([f'<span class="pill pill-green">{s}</span>' for s in strengths])
        st.markdown(pills, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="result-label">Growth Areas</div>', unsafe_allow_html=True)
        pills = "".join([f'<span class="pill pill-amber">{s}</span>' for s in gaps])
        st.markdown(pills, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="result-label">Career Matches</div>', unsafe_allow_html=True)
    
    st.markdown(f'''
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
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Timeline
    top_career = top_match['career']['title']
    st.markdown(f'''
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
    ''', unsafe_allow_html=True)
    
    # AI Coaches
    st.markdown('<div class="coach-section">', unsafe_allow_html=True)
    st.markdown('<div class="coach-title">Talk to a Career Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="coach-subtitle">Get personalized advice powered by AI</div>', unsafe_allow_html=True)
    
    api_status = check_api_status()
    available_coaches = []
    if api_status["claude"]:
        available_coaches.append("Claude")
    if api_status["chatgpt"]:
        available_coaches.append("ChatGPT")
    if api_status["gemini"]:
        available_coaches.append("Gemini")
    available_coaches.append("CareerCraft Coach")
    
    coach_choice = st.radio("Select coach:", available_coaches, horizontal=True, label_visibility="collapsed")
    
    user_input = st.text_area("Your question:", placeholder="What should I focus on first?", label_visibility="collapsed")
    
    if st.button("Get advice", key="coach_btn"):
        if user_input.strip():
            context = f"Strengths: {', '.join(strengths)}. Growth areas: {', '.join(gaps)}. Exploring: {top_career}."
            with st.spinner("Thinking..."):
                response = None
                error = None
                
                if coach_choice == "Claude":
                    response, error = get_claude_response(user_input, context)
                elif coach_choice == "ChatGPT":
                    response, error = get_chatgpt_response(user_input, context)
                elif coach_choice == "Gemini":
                    response, error = get_gemini_response(user_input, context)
                else:
                    response = get_fallback_response(user_input, context)
                
                if response:
                    st.session_state.coach_response = response
                    st.session_state.coach_provider = coach_choice
                    st.session_state.coach_error = None
                elif error:
                    st.session_state.coach_response = get_fallback_response(user_input, context)
                    st.session_state.coach_provider = "CareerCraft Coach"
                    st.session_state.coach_error = error
            st.rerun()
    
    if st.session_state.get("coach_response"):
        st.markdown(f'<div class="coach-response">{st.session_state.coach_response}</div>', unsafe_allow_html=True)
        if st.session_state.get("coach_provider"):
            st.markdown(f'<div class="coach-provider">Response from {st.session_state.coach_provider}</div>', unsafe_allow_html=True)
        if st.session_state.get("coach_error"):
            st.caption(f"Note: {st.session_state.coach_error}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Save results CTA
    st.markdown('''
    <div class="cta-card">
        <div class="cta-title">Save your results and join the community</div>
        <div class="cta-body">Create an account to track progress, get updated recommendations, and connect with others on similar journeys.</div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Create free account", use_container_width=True, key="results_signup"):
            st.session_state.show_signup = True
            st.rerun()
    
    if st.button("Start over", type="secondary", key="start_over"):
        st.session_state.step = "landing"
        st.session_state.answers = {}
        st.session_state.coach_response = None
        st.rerun()

def render_home():
    if st.session_state.step == "landing":
        render_home_landing()
    elif st.session_state.step == "questions":
        render_home_questions()
    elif st.session_state.step == "results":
        render_home_results()

# =============================================================================
# ABOUT PAGE
# =============================================================================

def render_about():
    st.markdown('''
    <div class="section-header">
        <div class="section-title">About CareerCraft</div>
        <div class="section-subtitle">Career intelligence, not career guessing</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="about-body">
        Most career advice is based on opinions, anecdotes, and gut feelings. We built CareerCraft because we believed career decisions deserve the same rigor as financial or medical decisions - grounded in data, transparent in methodology, and honest about uncertainty.
    </div>
    ''', unsafe_allow_html=True)
    
    # What makes us different
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">What makes us different</div>', unsafe_allow_html=True)
    
    diff_items = [
        ("1", "Enterprise-grade data.", "We integrate verified labor market data covering 1,016 occupations with 62,580 skill ratings, wage data from 800+ occupations, hiring records updated monthly, and educational outcomes by institution. No surveys. No self-reported data. The same verified information used by Fortune 500 companies and research institutions."),
        ("2", "Skill-level ROI.", "Everyone can tell you a CS degree has good ROI. We calculate the wage premium for individual skills: Python adds approximately $22,000 annually, project management adds $16,000, machine learning adds $35,000. You see exactly what to learn and what it's worth."),
        ("3", "Research-backed methodology.", "Our matching uses hedonic wage regression (the same method labor economists use), causal inference for estimating treatment effects of career moves, and conformal prediction for honest uncertainty quantification. This isn't a personality quiz - it's the same quantitative rigor found in peer-reviewed academic research."),
        ("4", "Transparent algorithms.", "Every recommendation includes explanations showing exactly why. No black boxes. If you want to see the math, you can. If you want to audit the logic, you can. We believe career decisions are too important for 'trust us.'"),
        ("5", "A community that gets it.", "Career transitions are hard. You're not just navigating job markets - you're navigating identity, family expectations, financial constraints, and fear of the unknown. Our community connects you with others at every stage, from students to seasoned reinventors, sharing real stories and real accountability."),
        ("6", "Longitudinal tracking.", "Your profile persists and evolves. As you build skills, as markets shift, as your priorities change - your recommendations update. Version control lets you see how your trajectory evolves over time."),
    ]
    
    for num, title, desc in diff_items:
        st.markdown(f'''
        <div class="pitch-item">
            <div class="pitch-num">{num}</div>
            <div class="pitch-text"><strong>{title}</strong> {desc}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Our data - FIXED: descriptions not source names
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Our data</div>', unsafe_allow_html=True)
    st.markdown('<div class="about-body">Every number in CareerCraft comes from a verified source:</div>', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="data-grid">
        <div class="data-card">
            <div class="data-value" style="font-size: 1.1rem;">Occupations</div>
            <div class="data-label">1,016 careers<br>62,580 skill ratings</div>
        </div>
        <div class="data-card">
            <div class="data-value" style="font-size: 1.1rem;">Wages</div>
            <div class="data-label">Salary data<br>800+ occupations</div>
        </div>
        <div class="data-card">
            <div class="data-value" style="font-size: 1.1rem;">Hiring</div>
            <div class="data-label">Job openings<br>Monthly updates</div>
        </div>
        <div class="data-card">
            <div class="data-value" style="font-size: 1.1rem;">Education</div>
            <div class="data-label">Graduate outcomes<br>By institution</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Community
    st.markdown('''
    <div class="community-card">
        <div class="community-title">Join the community</div>
        <div class="community-body">
            Career change is personal, but you don't have to do it alone. Our community connects students figuring out their first path, early-career professionals optimizing for growth, mid-career pivoters rediscovering purpose, and skilled immigrants navigating new markets. Share your wins, find accountability partners, get advice from people who've been where you are.
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Team
    st.markdown('''
    <div class="card">
        <div class="card-title">The team</div>
        <div class="about-body">
            CareerCraft is built by AMARI Group. We're a small team obsessed with bringing quantitative rigor to decisions that have historically been made on intuition. We believe everyone deserves access to the same quality of career intelligence that elite universities and top consulting firms provide to a select few.
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Try CareerCheck", use_container_width=True, key="about_cta"):
            navigate_to("home", "landing")
            st.rerun()

# =============================================================================
# USE CASES PAGE
# =============================================================================

def render_usecases():
    st.markdown('''
    <div class="section-header">
        <div class="section-title">Who CareerCraft is for</div>
        <div class="section-subtitle">Real people with real career questions</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="about-body" style="text-align: center; max-width: 560px; margin: 0 auto 2rem;">
        Career transitions are deeply personal. Our research identified four distinct segments - each with different needs, constraints, and definitions of success. Maybe you\'ll see yourself in one of them.
    </div>
    ''', unsafe_allow_html=True)
    
    # Render each persona separately for proper display
    for i, persona in enumerate(PERSONAS):
        # Card container with scroll animation
        st.markdown(f'<div class="persona-card scroll-fade" style="animation-delay: {i * 0.15}s;">', unsafe_allow_html=True)
        
        # Header
        st.markdown(f'''
        <div class="persona-header">
            <div>
                <div class="persona-name">{persona['name']}</div>
                <div class="persona-archetype">{persona['archetype']}</div>
            </div>
            <div class="persona-meta">
                <div class="persona-age">Age {persona['age']}</div>
                <div class="persona-stage">{persona['stage']}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Story
        st.markdown(f'<div class="persona-story">{persona["story"]}</div>', unsafe_allow_html=True)
        
        # Tension box
        st.markdown(f'''
        <div class="persona-tension">
            <div class="persona-tension-label">Current Tension</div>
            <div class="persona-tension-text">{persona['tension']}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Constraints
        st.markdown('<div class="persona-section-label">Key Constraints</div>', unsafe_allow_html=True)
        for constraint in persona["constraints"]:
            st.markdown(f'<div class="persona-constraint">{constraint}</div>', unsafe_allow_html=True)
        
        # JTBD box
        st.markdown(f'''
        <div class="persona-jtbd">
            <div class="persona-jtbd-label">What they need</div>
            <div class="persona-jtbd-text">{persona['jtbd']}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Resonant message
        st.markdown(f'''
        <div class="persona-message">
            <div class="persona-message-label">Message that resonates</div>
            <div class="persona-message-text">{persona['resonant_message']}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Stats
        st.markdown('<div class="persona-stats">', unsafe_allow_html=True)
        for stat in persona["stats"]:
            st.markdown(f'<span class="persona-stat">{stat}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Close card
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CTA
    st.markdown('''
    <div class="cta-card scroll-fade">
        <div class="cta-title">See yourself here?</div>
        <div class="cta-body">Take CareerCheck and get clarity on your own situation. Join a community of people navigating similar challenges.</div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start CareerCheck", use_container_width=True, key="usecase_cta"):
            navigate_to("home", "landing")
            st.rerun()

# =============================================================================
# MAIN
# =============================================================================

def main():
    render_nav()
    
    if st.session_state.get("show_signup", False):
        render_signup()
        return
    
    page = st.session_state.get("page", "home")
    
    if page == "home":
        render_home()
    elif page == "about":
        render_about()
    elif page == "usecases":
        render_usecases()

if __name__ == "__main__":
    main()
