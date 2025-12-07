"""
CareerCraft – Career Intelligence Platform
Multi-interface application with methodology transparency
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
        "range": "$95k-$180k", "median": 137000, "growth": 10,
        "description": "Product Managers own the strategy and roadmap for products, working at the intersection of business, technology, and user experience.",
        "fit": {"technical": 60, "people_energy": 80, "people_style": 75, "analysis": 70, "structure": 60, "learning": 80, "client_facing": 70},
        "top_skills": ["Strategic thinking", "Communication", "Data analysis", "User research", "Roadmap planning"],
        "education": "Bachelor's degree typical, MBA common",
        "source": "BLS OEWS 2024"
    },
    {
        "id": "dev", "title": "Software Developer", "subtitle": "Build and create",
        "range": "$80k-$200k", "median": 132000, "growth": 17,
        "description": "Software Developers design, build, and maintain applications and systems that power modern technology.",
        "fit": {"technical": 95, "people_energy": 40, "people_style": 45, "analysis": 80, "structure": 70, "learning": 90, "client_facing": 30},
        "top_skills": ["Programming", "Problem solving", "System design", "Version control", "Testing"],
        "education": "Bachelor's in CS or self-taught with portfolio",
        "source": "BLS OEWS 2024"
    },
    {
        "id": "data", "title": "Data Analyst", "subtitle": "Find insights in numbers",
        "range": "$65k-$130k", "median": 86000, "growth": 23,
        "description": "Data Analysts collect, process, and analyze data to help organizations make informed decisions.",
        "fit": {"technical": 85, "people_energy": 45, "people_style": 40, "analysis": 95, "structure": 80, "learning": 70, "client_facing": 50},
        "top_skills": ["SQL", "Statistical analysis", "Data visualization", "Excel", "Python/R"],
        "education": "Bachelor's in quantitative field",
        "source": "BLS OEWS 2024"
    },
    {
        "id": "ux", "title": "UX Designer", "subtitle": "Design for humans",
        "range": "$70k-$150k", "median": 98000, "growth": 16,
        "description": "UX Designers research user needs and design intuitive, accessible digital experiences.",
        "fit": {"technical": 50, "people_energy": 70, "people_style": 55, "analysis": 60, "structure": 50, "learning": 80, "client_facing": 75},
        "top_skills": ["User research", "Wireframing", "Prototyping", "Visual design", "Usability testing"],
        "education": "Bachelor's or bootcamp with strong portfolio",
        "source": "BLS OEWS 2024"
    },
    {
        "id": "marketing", "title": "Marketing Manager", "subtitle": "Tell compelling stories",
        "range": "$75k-$160k", "median": 140000, "growth": 7,
        "description": "Marketing Managers develop and execute strategies to promote products and build brand awareness.",
        "fit": {"technical": 40, "people_energy": 85, "people_style": 70, "analysis": 50, "structure": 50, "learning": 70, "client_facing": 85},
        "top_skills": ["Brand strategy", "Content creation", "Analytics", "Campaign management", "Communication"],
        "education": "Bachelor's in Marketing or Business",
        "source": "BLS OEWS 2024"
    },
    {
        "id": "consultant", "title": "Consultant", "subtitle": "Solve business problems",
        "range": "$80k-$170k", "median": 99000, "growth": 11,
        "description": "Consultants advise organizations on strategy, operations, and specific business challenges.",
        "fit": {"technical": 60, "people_energy": 80, "people_style": 75, "analysis": 75, "structure": 70, "learning": 90, "client_facing": 95},
        "top_skills": ["Problem solving", "Presentation", "Analysis", "Client management", "Industry expertise"],
        "education": "Bachelor's degree, MBA valued",
        "source": "BLS OEWS 2024"
    },
    {
        "id": "analyst", "title": "Business Analyst", "subtitle": "Bridge tech and business",
        "range": "$70k-$130k", "median": 95000, "growth": 14,
        "description": "Business Analysts translate business needs into technical requirements and process improvements.",
        "fit": {"technical": 70, "people_energy": 65, "people_style": 50, "analysis": 85, "structure": 75, "learning": 75, "client_facing": 60},
        "top_skills": ["Requirements gathering", "Process modeling", "Documentation", "SQL", "Stakeholder management"],
        "education": "Bachelor's in Business or IT",
        "source": "BLS OEWS 2024"
    },
    {
        "id": "manager", "title": "People Manager", "subtitle": "Lead and develop teams",
        "range": "$90k-$170k", "median": 120000, "growth": 8,
        "description": "People Managers lead teams, develop talent, and drive organizational performance.",
        "fit": {"technical": 45, "people_energy": 90, "people_style": 95, "analysis": 55, "structure": 70, "learning": 65, "client_facing": 60},
        "top_skills": ["Leadership", "Coaching", "Performance management", "Conflict resolution", "Strategic planning"],
        "education": "Bachelor's degree plus experience",
        "source": "BLS OEWS 2024"
    },
]

SKILLS_DATA = {
    "Python": {"category": "Technical", "premium": 22000, "growth": "High", "demand": 94},
    "SQL": {"category": "Technical", "premium": 15000, "growth": "Stable", "demand": 89},
    "Data Analysis": {"category": "Technical", "premium": 18000, "growth": "High", "demand": 87},
    "Machine Learning": {"category": "Technical", "premium": 35000, "growth": "Very High", "demand": 78},
    "Cloud Computing": {"category": "Technical", "premium": 28000, "growth": "Very High", "demand": 82},
    "Project Management": {"category": "Business", "premium": 16000, "growth": "Stable", "demand": 85},
    "Communication": {"category": "Soft", "premium": 12000, "growth": "Stable", "demand": 95},
    "Leadership": {"category": "Soft", "premium": 25000, "growth": "Stable", "demand": 80},
    "Strategic Thinking": {"category": "Business", "premium": 20000, "growth": "Growing", "demand": 76},
    "User Research": {"category": "Design", "premium": 14000, "growth": "Growing", "demand": 68},
}

MARKET_DATA = {
    "Technology": {"hiring": "Strong", "yoy_change": 8, "openings": 1240000, "avg_salary": 125000},
    "Healthcare": {"hiring": "Very Strong", "yoy_change": 12, "openings": 980000, "avg_salary": 78000},
    "Finance": {"hiring": "Moderate", "yoy_change": 3, "openings": 520000, "avg_salary": 95000},
    "Consulting": {"hiring": "Strong", "yoy_change": 6, "openings": 180000, "avg_salary": 105000},
    "Marketing": {"hiring": "Moderate", "yoy_change": 4, "openings": 340000, "avg_salary": 72000},
}

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
        max-width: 720px;
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
    .nav-container {
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
    
    /* Tabs */
    .nav-tabs {
        display: flex;
        gap: 0.25rem;
        background: #f0ede8;
        padding: 0.25rem;
        border-radius: 8px;
    }
    
    .nav-tab {
        padding: 0.5rem 0.9rem;
        font-size: 0.8rem;
        font-weight: 500;
        color: #666;
        background: transparent;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .nav-tab:hover {
        color: #1a1a1a;
        background: rgba(255,255,255,0.5);
    }
    
    .nav-tab.active {
        background: white;
        color: #1a1a1a;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
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
    
    .card-header {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .card-meta {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.75rem;
    }
    
    .card-body {
        font-size: 0.9rem;
        color: #444;
        line-height: 1.55;
    }
    
    /* Data cards */
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
    
    /* Result cards */
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
    .pill-blue { background: #e8f4fd; color: #1d4ed8; }
    
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
    
    /* Signup section */
    .signup-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid #e8e5e0;
    }
    
    .signup-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .signup-title {
        font-family: 'Fraunces', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .signup-subtitle {
        font-size: 0.95rem;
        color: #555;
    }
    
    .pitch-section {
        background: #f8f8f6;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1.25rem 0;
    }
    
    .pitch-title {
        font-family: 'Fraunces', serif;
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.75rem;
    }
    
    .pitch-item {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        color: #2d2d2d;
        line-height: 1.45;
    }
    
    .pitch-icon {
        width: 20px;
        height: 20px;
        background: #4A6741;
        border-radius: 50%;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.65rem;
        margin-top: 0.1rem;
    }
    
    .data-sources {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .data-source {
        background: white;
        border: 1px solid #e8e5e0;
        border-radius: 6px;
        padding: 0.4rem 0.75rem;
        font-size: 0.75rem;
        color: #555;
    }
    
    /* Career card */
    .career-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid #e8e5e0;
        transition: all 0.2s;
    }
    
    .career-card:hover {
        border-color: #4A6741;
        box-shadow: 0 4px 12px rgba(74, 103, 65, 0.1);
    }
    
    .career-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.75rem;
    }
    
    .career-title {
        font-family: 'Fraunces', serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.15rem;
    }
    
    .career-subtitle {
        font-size: 0.85rem;
        color: #666;
    }
    
    .career-salary {
        text-align: right;
    }
    
    .career-salary-value {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #4A6741;
    }
    
    .career-salary-label {
        font-size: 0.7rem;
        color: #888;
    }
    
    .career-stats {
        display: flex;
        gap: 1.5rem;
        margin: 0.75rem 0;
        padding: 0.75rem 0;
        border-top: 1px solid #f0ede8;
        border-bottom: 1px solid #f0ede8;
    }
    
    .career-stat {
        text-align: center;
    }
    
    .career-stat-value {
        font-weight: 600;
        color: #1a1a1a;
        font-size: 0.95rem;
    }
    
    .career-stat-label {
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .career-skills {
        margin-top: 0.75rem;
    }
    
    .career-skills-label {
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.4rem;
    }
    
    /* Skill row */
    .skill-row {
        background: white;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.6rem;
        border: 1px solid #e8e5e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .skill-info {
        flex: 1;
    }
    
    .skill-name {
        font-weight: 600;
        color: #1a1a1a;
        font-size: 0.95rem;
        margin-bottom: 0.15rem;
    }
    
    .skill-category {
        font-size: 0.75rem;
        color: #888;
    }
    
    .skill-premium {
        text-align: right;
    }
    
    .skill-premium-value {
        font-family: 'Fraunces', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #4A6741;
    }
    
    .skill-premium-label {
        font-size: 0.65rem;
        color: #888;
    }
    
    .skill-demand {
        width: 60px;
        text-align: center;
        margin-left: 1rem;
    }
    
    .skill-demand-bar {
        height: 4px;
        background: #e8e5e0;
        border-radius: 2px;
        overflow: hidden;
        margin-bottom: 0.25rem;
    }
    
    .skill-demand-fill {
        height: 100%;
        background: #4A6741;
        border-radius: 2px;
    }
    
    .skill-demand-label {
        font-size: 0.65rem;
        color: #888;
    }
    
    /* Methodology section */
    .method-section {
        margin: 1.5rem 0;
    }
    
    .method-title {
        font-family: 'Fraunces', serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.75rem;
    }
    
    .method-body {
        font-size: 0.9rem;
        color: #444;
        line-height: 1.65;
        margin-bottom: 1rem;
    }
    
    .formula-box {
        background: #1a1a1a;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        font-family: 'SF Mono', 'Monaco', monospace;
        font-size: 0.85rem;
        color: #86efac;
        overflow-x: auto;
        margin: 0.75rem 0;
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
    
    .stSelectbox > div > div {
        background: white !important;
        border: 1.5px solid #d1d1d1 !important;
        border-radius: 8px !important;
    }
    
    .footer-note {
        text-align: center;
        font-size: 0.75rem;
        color: #888;
        margin-top: 1.25rem;
        font-style: italic;
    }
    
    /* Section header */
    .section-header {
        margin-bottom: 1.25rem;
    }
    
    .section-title {
        font-family: 'Fraunces', serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.35rem;
    }
    
    .section-subtitle {
        font-size: 0.95rem;
        color: #666;
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

COACH_SYSTEM = """You are a thoughtful career coach. Help people think through career decisions with:
1. What matters most right now
2. How to frame the next 3-6 months
3. 1-3 concrete, low-risk experiments
Keep responses under 200 words. Be warm but direct."""

def get_fallback_response(user_msg, context):
    """Always-available fallback when APIs aren't configured"""
    return f"""Based on your profile, here's how I'd approach this:

**Start with conversations, not courses.** Before investing in any training, talk to 2-3 people actually doing the work you're considering. Ask them: What surprised you about this role? What do you wish you'd known?

**Run a small experiment.** Pick one thing you can try in the next 2 weeks that tests your interest. Could be a side project, volunteering for a task at work, or taking a free introductory course.

**Your strengths are your foundation.** Build from what already works for you rather than trying to fix every gap at once. Look for roles that let you use your existing strengths while gradually building new skills.

The goal isn't to have perfect clarity—it's to learn enough to take the next small step with confidence.

What specific aspect would you like to explore further?"""

def get_claude_response(user_msg, context):
    api_key = get_secret("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "ANTHROPIC_API_KEY not found in secrets"
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
        return None, f"Claude API error: {str(e)}"

def get_chatgpt_response(user_msg, context):
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        return None, "OPENAI_API_KEY not found in secrets"
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
        return None, f"ChatGPT API error: {str(e)}"

def get_gemini_response(user_msg, context):
    api_key = get_secret("GOOGLE_API_KEY")
    if not api_key:
        return None, "GOOGLE_API_KEY not found in secrets"
    if not GEMINI_AVAILABLE:
        return None, "google-generativeai package not installed"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"{COACH_SYSTEM}\n\n{context}\n\nUser question: {user_msg}"
        resp = model.generate_content(prompt)
        return resp.text.strip(), None
    except Exception as e:
        return None, f"Gemini API error: {str(e)}"

def check_api_status():
    """Check which APIs are configured"""
    status = {}
    status["claude"] = bool(get_secret("ANTHROPIC_API_KEY")) and ANTHROPIC_AVAILABLE
    status["chatgpt"] = bool(get_secret("OPENAI_API_KEY")) and OPENAI_AVAILABLE
    status["gemini"] = bool(get_secret("GOOGLE_API_KEY")) and GEMINI_AVAILABLE
    return status

# =============================================================================
# SESSION STATE
# =============================================================================

if "page" not in st.session_state:
    st.session_state.page = "careercheck"
    st.session_state.step = "landing"
    st.session_state.question_idx = 0
    st.session_state.answers = {}
    st.session_state.coach_response = None
    st.session_state.coach_provider = None
    st.session_state.coach_error = None
    st.session_state.show_signup = False

# =============================================================================
# NAVIGATION
# =============================================================================

def render_nav():
    pages = [
        ("CareerCheck", "careercheck"),
        ("Careers", "careers"),
        ("Skills Lab", "skills"),
        ("Market", "market"),
        ("Methodology", "methodology"),
    ]
    
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("""
        <div class="logo">
            <div class="logo-mark">C</div>
            <div class="logo-text">CareerCraft</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cols = st.columns(len(pages) + 1)
        for i, (label, page_id) in enumerate(pages):
            with cols[i]:
                is_active = st.session_state.page == page_id
                if st.button(label, key=f"nav_{page_id}", type="secondary" if not is_active else "primary"):
                    st.session_state.page = page_id
                    st.rerun()
        
        with cols[-1]:
            if st.button("Sign up", key="nav_signup", type="secondary"):
                st.session_state.show_signup = True
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# SIGNUP PAGE
# =============================================================================

def render_signup():
    st.markdown("""
    <div class="signup-section">
        <div class="signup-header">
            <div class="signup-title">Join CareerCraft</div>
            <div class="signup-subtitle">Career intelligence powered by real data and proven methodology</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # The pitch
    st.markdown("""
    <div class="pitch-section">
        <div class="pitch-title">What makes CareerCraft different</div>
        
        <div class="pitch-item">
            <div class="pitch-icon">1</div>
            <div><strong>Government-grade data, not opinions.</strong> We integrate O*NET (1,016 occupations, 62,580 skill ratings), BLS wage data, JOLTS hiring records, and Census educational outcomes. Every recommendation is grounded in verified labor market data.</div>
        </div>
        
        <div class="pitch-item">
            <div class="pitch-icon">2</div>
            <div><strong>Skill-level ROI calculations.</strong> Most tools tell you a degree is "worth it." We calculate the specific wage premium for individual skills. Python adds ~$22,000/year. Project management adds ~$16,000. You see exactly what to learn.</div>
        </div>
        
        <div class="pitch-item">
            <div class="pitch-icon">3</div>
            <div><strong>PhD-level methodology.</strong> Our matching uses hedonic wage regression (Dey & Loewenstein), causal inference for treatment effects (Athey & Wager), and conformal prediction for uncertainty quantification. This isn't a quiz—it's econometric analysis.</div>
        </div>
        
        <div class="pitch-item">
            <div class="pitch-icon">4</div>
            <div><strong>Transparent algorithms.</strong> Every recommendation comes with SHAP explanations showing why. No black boxes. You can see the math, audit the logic, and understand exactly how we arrived at your results.</div>
        </div>
        
        <div class="pitch-item">
            <div class="pitch-icon">5</div>
            <div><strong>Longitudinal tracking.</strong> Your profile persists. As you build skills and the market shifts, your recommendations update. Version control lets you see how your trajectory evolves over time.</div>
        </div>
        
        <div style="margin-top: 1rem;">
            <div style="font-size: 0.8rem; color: #666; margin-bottom: 0.5rem; font-weight: 600;">DATA SOURCES</div>
            <div class="data-sources">
                <span class="data-source">O*NET 30.0</span>
                <span class="data-source">BLS OEWS</span>
                <span class="data-source">BLS JOLTS</span>
                <span class="data-source">Census PSEO</span>
                <span class="data-source">BLS Projections</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Form
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First name")
        with col2:
            last_name = st.text_input("Last name")
        
        email = st.text_input("Email address")
        password = st.text_input("Create password", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Create free account", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True, type="secondary"):
                st.session_state.show_signup = False
                st.rerun()
        
        if submitted and email and password:
            st.success("Account created! Welcome to CareerCraft.")
            st.session_state.show_signup = False
    
    st.markdown('<p class="footer-note">Free during beta. No credit card required.</p>', unsafe_allow_html=True)

# =============================================================================
# CAREERCHECK PAGE
# =============================================================================

def render_careercheck_landing():
    st.markdown("""
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
    """, unsafe_allow_html=True)
    
    st.markdown("""
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
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start CareerCheck", use_container_width=True):
            st.session_state.step = "questions"
            st.session_state.question_idx = 0
            st.session_state.answers = {}
            st.rerun()
    
    st.markdown('<p class="footer-note">No signup required to start.</p>', unsafe_allow_html=True)

def render_careercheck_questions():
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
            if st.button(option["label"], key=f"q_{question['id']}_{option['value']}", 
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

def render_careercheck_results():
    answers = st.session_state.answers
    matches = calculate_career_matches(answers)
    strengths, gaps = get_strengths_and_gaps(answers)
    
    top_match = matches[0]
    second_match = matches[1]
    third_match = matches[2]
    
    st.markdown("""
    <div class="section-header" style="text-align: center;">
        <div class="section-title">Your Results</div>
        <div class="section-subtitle">Based on your 7 answers</div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # AI Coaches
    st.markdown('<div class="coach-section">', unsafe_allow_html=True)
    st.markdown('<div class="coach-title">Talk to a Career Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="coach-subtitle">Get personalized advice powered by AI</div>', unsafe_allow_html=True)
    
    # Check API status
    api_status = check_api_status()
    
    # Show which coaches are available
    available_coaches = []
    if api_status["claude"]:
        available_coaches.append("Claude")
    if api_status["chatgpt"]:
        available_coaches.append("ChatGPT")
    if api_status["gemini"]:
        available_coaches.append("Gemini")
    available_coaches.append("CareerCraft Coach")  # Always available fallback
    
    coach_choice = st.radio("Select coach:", available_coaches, horizontal=True, label_visibility="collapsed")
    
    user_input = st.text_area("Your question:", placeholder="What should I focus on first?", label_visibility="collapsed")
    
    if st.button("Get advice"):
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
                    # CareerCraft Coach fallback
                    response = get_fallback_response(user_input, context)
                    error = None
                
                if response:
                    st.session_state.coach_response = response
                    st.session_state.coach_provider = coach_choice
                    st.session_state.coach_error = None
                elif error:
                    # Try fallback on error
                    st.session_state.coach_response = get_fallback_response(user_input, context)
                    st.session_state.coach_provider = "CareerCraft Coach"
                    st.session_state.coach_error = error
            st.rerun()
    
    if st.session_state.get("coach_response"):
        st.markdown(f'<div class="coach-response">{st.session_state.coach_response}</div>', unsafe_allow_html=True)
        provider = st.session_state.get("coach_provider", "")
        if provider:
            st.markdown(f'<div class="coach-provider">Response from {provider}</div>', unsafe_allow_html=True)
        
        # Show error if there was one (for debugging)
        if st.session_state.get("coach_error"):
            st.caption(f"Note: {st.session_state.coach_error} - Using fallback coach instead.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Save results CTA
    st.markdown('<div class="card" style="text-align: center; background: linear-gradient(135deg, #f5faf4 0%, #f0f7ff 100%);">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Save your results</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-body">Create an account to track progress and get updated recommendations.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Create free account", use_container_width=True, key="results_signup"):
            st.session_state.show_signup = True
            st.rerun()
    
    if st.button("Start over", type="secondary"):
        st.session_state.step = "landing"
        st.session_state.answers = {}
        st.session_state.coach_response = None
        st.rerun()

def render_careercheck():
    if st.session_state.step == "landing":
        render_careercheck_landing()
    elif st.session_state.step == "questions":
        render_careercheck_questions()
    elif st.session_state.step == "results":
        render_careercheck_results()

# =============================================================================
# CAREERS PAGE
# =============================================================================

def render_careers():
    st.markdown("""
    <div class="section-header">
        <div class="section-title">Career Explorer</div>
        <div class="section-subtitle">Browse careers with real salary and growth data from BLS</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("Sort by", ["Salary (high to low)", "Growth rate", "Alphabetical"])
    with col2:
        min_salary = st.selectbox("Minimum salary", ["Any", "$70k+", "$90k+", "$120k+"])
    
    # Sort careers
    sorted_careers = CAREERS.copy()
    if sort_by == "Salary (high to low)":
        sorted_careers.sort(key=lambda x: x["median"], reverse=True)
    elif sort_by == "Growth rate":
        sorted_careers.sort(key=lambda x: x["growth"], reverse=True)
    else:
        sorted_careers.sort(key=lambda x: x["title"])
    
    # Filter
    if min_salary == "$70k+":
        sorted_careers = [c for c in sorted_careers if c["median"] >= 70000]
    elif min_salary == "$90k+":
        sorted_careers = [c for c in sorted_careers if c["median"] >= 90000]
    elif min_salary == "$120k+":
        sorted_careers = [c for c in sorted_careers if c["median"] >= 120000]
    
    for career in sorted_careers:
        st.markdown(f"""
        <div class="career-card">
            <div class="career-header">
                <div>
                    <div class="career-title">{career['title']}</div>
                    <div class="career-subtitle">{career['subtitle']}</div>
                </div>
                <div class="career-salary">
                    <div class="career-salary-value">${career['median']:,}</div>
                    <div class="career-salary-label">median salary</div>
                </div>
            </div>
            <div class="card-body">{career['description']}</div>
            <div class="career-stats">
                <div class="career-stat">
                    <div class="career-stat-value">{career['growth']}%</div>
                    <div class="career-stat-label">Growth (10yr)</div>
                </div>
                <div class="career-stat">
                    <div class="career-stat-value">{career['range']}</div>
                    <div class="career-stat-label">Salary Range</div>
                </div>
                <div class="career-stat">
                    <div class="career-stat-value">{career['education'].split()[0]}</div>
                    <div class="career-stat-label">Education</div>
                </div>
            </div>
            <div class="career-skills">
                <div class="career-skills-label">Top Skills</div>
                {"".join([f'<span class="pill pill-blue">{s}</span>' for s in career['top_skills'][:4]])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f'<p class="footer-note">Salary data from {CAREERS[0]["source"]}</p>', unsafe_allow_html=True)

# =============================================================================
# SKILLS LAB PAGE
# =============================================================================

def render_skills():
    st.markdown("""
    <div class="section-header">
        <div class="section-title">Skills Lab</div>
        <div class="section-subtitle">See the wage premium for each skill based on labor market data</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <div class="card-header">How skill premiums work</div>
        <div class="card-body">
            We calculate skill premiums using hedonic wage regression—the same methodology labor economists use.
            By analyzing wage data across occupations that require each skill (from O*NET) against BLS salary data,
            we isolate the marginal value each skill adds to your earning potential.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter
    category_filter = st.selectbox("Filter by category", ["All", "Technical", "Business", "Soft", "Design"])
    
    filtered_skills = SKILLS_DATA.items()
    if category_filter != "All":
        filtered_skills = [(k, v) for k, v in filtered_skills if v["category"] == category_filter]
    
    # Sort by premium
    sorted_skills = sorted(filtered_skills, key=lambda x: x[1]["premium"], reverse=True)
    
    for skill_name, skill_data in sorted_skills:
        st.markdown(f"""
        <div class="skill-row">
            <div class="skill-info">
                <div class="skill-name">{skill_name}</div>
                <div class="skill-category">{skill_data['category']} | Growth: {skill_data['growth']}</div>
            </div>
            <div class="skill-premium">
                <div class="skill-premium-value">+${skill_data['premium']:,}</div>
                <div class="skill-premium-label">annual premium</div>
            </div>
            <div class="skill-demand">
                <div class="skill-demand-bar">
                    <div class="skill-demand-fill" style="width: {skill_data['demand']}%"></div>
                </div>
                <div class="skill-demand-label">{skill_data['demand']}% demand</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<p class="footer-note">Premiums calculated from O*NET skill ratings cross-referenced with BLS OEWS wage data</p>', unsafe_allow_html=True)

# =============================================================================
# MARKET PAGE
# =============================================================================

def render_market():
    st.markdown("""
    <div class="section-header">
        <div class="section-title">Market Pulse</div>
        <div class="section-subtitle">Labor market trends from BLS JOLTS data</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="data-grid">
        <div class="data-card">
            <div class="data-value">11.2M</div>
            <div class="data-label">Job Openings</div>
        </div>
        <div class="data-card">
            <div class="data-value">3.7%</div>
            <div class="data-label">Unemployment</div>
        </div>
        <div class="data-card">
            <div class="data-value">+2.1%</div>
            <div class="data-label">Wage Growth YoY</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card"><div class="card-header">Industry Outlook</div></div>', unsafe_allow_html=True)
    
    for industry, data in MARKET_DATA.items():
        hiring_color = "#4A6741" if data["hiring"] in ["Strong", "Very Strong"] else "#d97706"
        st.markdown(f"""
        <div class="skill-row">
            <div class="skill-info">
                <div class="skill-name">{industry}</div>
                <div class="skill-category">{data['openings']:,} openings | Avg ${data['avg_salary']:,}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 600; color: {hiring_color};">{data['hiring']}</div>
                <div style="font-size: 0.75rem; color: #888;">{'+' if data['yoy_change'] > 0 else ''}{data['yoy_change']}% YoY</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<p class="footer-note">Data from BLS JOLTS, updated monthly</p>', unsafe_allow_html=True)

# =============================================================================
# METHODOLOGY PAGE
# =============================================================================

def render_methodology():
    st.markdown("""
    <div class="section-header">
        <div class="section-title">Our Methodology</div>
        <div class="section-subtitle">The science behind CareerCraft recommendations</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="method-section">
        <div class="method-title">Data Sources</div>
        <div class="method-body">
            CareerCraft integrates four major government datasets to ensure recommendations are grounded in verified labor market reality:
        </div>
        <div class="data-grid">
            <div class="data-card">
                <div class="data-value" style="font-size: 1.1rem;">O*NET 30.0</div>
                <div class="data-label">1,016 occupations<br>62,580 skill ratings</div>
            </div>
            <div class="data-card">
                <div class="data-value" style="font-size: 1.1rem;">BLS OEWS</div>
                <div class="data-label">Wage data<br>800+ occupations</div>
            </div>
            <div class="data-card">
                <div class="data-value" style="font-size: 1.1rem;">BLS JOLTS</div>
                <div class="data-label">Hiring trends<br>Monthly updates</div>
            </div>
            <div class="data-card">
                <div class="data-value" style="font-size: 1.1rem;">Census PSEO</div>
                <div class="data-label">Education outcomes<br>By institution</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="method-section">
        <div class="method-title">Skill Premium Calculation</div>
        <div class="method-body">
            We calculate wage premiums for individual skills using hedonic wage regression, following the methodology established by Dey and Loewenstein. This isolates the marginal contribution of each skill to wages while controlling for occupation, education, and experience.
        </div>
        <div class="formula-box">
ln(wage) = α + Σβₖ(skill_k) + γX + ε

where:
  skill_k = O*NET importance rating for skill k
  X = control variables (education, experience, region)
  βₖ = wage premium attributable to skill k
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="method-section">
        <div class="method-title">Career Matching Algorithm</div>
        <div class="method-body">
            Career matches are calculated using a weighted distance function across seven dimensions. Each career has an ideal profile based on O*NET work context ratings. Your assessment responses are compared against these profiles to generate match percentages.
        </div>
        <div class="formula-box">
match_score = 100 - (Σ|user_d - career_d| / max_diff) × 100

where:
  user_d = user's score on dimension d
  career_d = career's ideal score on dimension d
  max_diff = maximum possible total difference
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="method-section">
        <div class="method-title">Uncertainty Quantification</div>
        <div class="method-body">
            We use conformal prediction (Romano et al., 2019) to provide calibrated uncertainty intervals on salary projections and career trajectory forecasts. This ensures we communicate confidence appropriately rather than providing false precision.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="method-section">
        <div class="method-title">Causal Inference</div>
        <div class="method-body">
            When estimating the effect of interventions (education, certifications, job changes), we apply causal forest methodology (Athey & Wager, 2019) to estimate heterogeneous treatment effects. This allows us to personalize ROI estimates rather than relying on population averages.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card" style="background: #f8f8f6;">
        <div class="card-header">Academic References</div>
        <div class="card-body" style="font-size: 0.85rem; line-height: 1.7;">
            Athey, S., & Wager, S. (2019). Estimating treatment effects with causal forests. <em>Journal of the American Statistical Association.</em><br><br>
            Dey, M., & Loewenstein, M. (2020). How many workers are employed in sectors directly affected by COVID-19 shutdowns? <em>Monthly Labor Review, BLS.</em><br><br>
            Romano, Y., Patterson, E., & Candès, E. (2019). Conformalized quantile regression. <em>NeurIPS.</em><br><br>
            Hamilton, W. L., Ying, R., & Leskovec, J. (2017). Inductive representation learning on large graphs. <em>NeurIPS.</em>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="footer-note">Full methodology documentation available for academic partners</p>', unsafe_allow_html=True)

# =============================================================================
# MAIN
# =============================================================================

def main():
    # Check for signup modal first
    if st.session_state.get("show_signup", False):
        render_nav()
        render_signup()
        return
    
    render_nav()
    
    page = st.session_state.get("page", "careercheck")
    
    if page == "careercheck":
        render_careercheck()
    elif page == "careers":
        render_careers()
    elif page == "skills":
        render_skills()
    elif page == "market":
        render_market()
    elif page == "methodology":
        render_methodology()

if __name__ == "__main__":
    main()
