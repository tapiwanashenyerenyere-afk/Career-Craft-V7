"""
CareerCraft V7 - Streamlit Application
Fixed version with correct model names and safe secrets access
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# Optional imports - graceful fallback if not installed
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

# -------------------------
# PAGE CONFIG & GLOBAL STYLE
# -------------------------

st.set_page_config(
    page_title="CareerCraft – CareerCheck",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Global CSS: white product feel, centred content
st.markdown(
    """
    <style>
    body {
        background-color: #f5f7fb;
        color: #0f172a;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .main .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3.5rem;
        max-width: 1100px;
    }
    .hero-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 28px 32px 26px 32px;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
        border: 1px solid rgba(148, 163, 184, 0.28);
    }
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.28rem 0.78rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 500;
        background: #ecfdf5;
        color: #16a34a;
        border: 1px solid rgba(22, 163, 74, 0.18);
    }
    .pill-dot {
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #22c55e;
        box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.45);
    }
    .hero-title {
        font-size: 2.1rem;
        line-height: 1.15;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-top: 0.8rem;
        margin-bottom: 0.65rem;
        color: #020617;
    }
    .hero-sub {
        font-size: 0.99rem;
        line-height: 1.55;
        color: #4b5563;
    }
    .hero-grid {
        margin-top: 1.6rem;
        display: grid;
        grid-template-columns: 1.3fr 1fr 1fr;
        gap: 1.2rem;
    }
    @media (max-width: 768px) {
        .hero-grid {
            grid-template-columns: 1fr;
        }
    }
    .hero-pill-col-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 0.35rem;
        font-weight: 600;
    }
    .hero-pill-col-body {
        font-size: 0.9rem;
        line-height: 1.45;
        color: #111827;
    }
    .hero-footnote {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-top: 0.9rem;
    }
    .cc-secondary-text {
        font-size: 0.82rem;
        color: #6b7280;
        margin-top: 0.45rem;
    }
    .entry-row {
        margin-top: 2.1rem;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.3rem;
    }
    @media (max-width: 768px) {
        .entry-row {
            grid-template-columns: 1fr;
        }
    }
    .entry-card {
        background: #020617;
        color: #e5e7eb;
        border-radius: 16px;
        padding: 1rem 1.3rem 1.1rem 1.3rem;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.55);
        position: relative;
        overflow: hidden;
    }
    .entry-pill-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #9ca3af;
        margin-bottom: 0.25rem;
    }
    .entry-title {
        font-size: 1.02rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .entry-body {
        font-size: 0.86rem;
        color: #e5e7eb;
        opacity: 0.9;
        margin-bottom: 0.65rem;
    }
    .entry-cta {
        font-size: 0.82rem;
        color: #f97316;
        font-weight: 500;
    }
    .entry-emoji {
        position: absolute;
        font-size: 1.25rem;
        opacity: 0.55;
    }
    .entry-emoji.left {
        left: 0.9rem;
        bottom: 0.55rem;
    }
    .entry-emoji.right {
        right: 0.85rem;
        top: 0.65rem;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 0.4rem;
        color: #020617;
    }
    .section-caption {
        font-size: 0.88rem;
        color: #6b7280;
        margin-bottom: 0.7rem;
    }
    .skill-chip {
        display: inline-flex;
        padding: 0.22rem 0.6rem;
        border-radius: 999px;
        background: #eff6ff;
        color: #1d4ed8;
        font-size: 0.78rem;
        margin-right: 0.35rem;
        margin-bottom: 0.25rem;
    }
    .direction-card {
        border-radius: 14px;
        padding: 0.9rem 1rem;
        background: #ffffff;
        border-left: 4px solid #22c55e;
        margin-bottom: 0.7rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
    }
    .direction-card.lateral { border-left-color: #0ea5e9; }
    .direction-card.stretch { border-left-color: #f97316; }
    .direction-header {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.1rem;
    }
    .direction-meta {
        font-size: 0.78rem;
        color: #6b7280;
        margin-bottom: 0.35rem;
    }
    .direction-body {
        font-size: 0.86rem;
        color: #111827;
    }
    .pill-readiness {
        display: inline-flex;
        align-items: center;
        padding: 0.1rem 0.5rem;
        border-radius: 999px;
        font-size: 0.74rem;
        margin-left: 0.4rem;
        background: #ecfdf5;
        color: #15803d;
    }
    .pill-readiness.stretch {
        background: #fff7ed;
        color: #c2410c;
    }
    .pill-readiness.longshot {
        background: #f5f3ff;
        color: #6d28d9;
    }
    .sprint-box {
        background: #0f172a;
        color: #e5e7eb;
        border-radius: 16px;
        padding: 0.95rem 1.05rem;
        font-size: 0.9rem;
        box-shadow: 0 16px 35px rgba(15, 23, 42, 0.6);
    }
    .sprint-tag {
        font-size: 0.75rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 0.35rem;
    }
    .sprint-title {
        font-size: 0.98rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .sprint-body {
        font-size: 0.86rem;
        color: #d1d5db;
    }
    .coach-box {
        background: #ffffff;
        border-radius: 16px;
        padding: 0.9rem 1.0rem;
        border: 1px solid rgba(148, 163, 184, 0.4);
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.04);
    }
    .coach-title {
        font-size: 0.98rem;
        font-weight: 600;
        margin-bottom: 0.1rem;
    }
    .coach-caption {
        font-size: 0.82rem;
        color: #6b7280;
        margin-bottom: 0.4rem;
    }
    .coach-reply {
        font-size: 0.9rem;
        color: #111827;
        margin-top: 0.45rem;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------
# HELPER: SAFE SECRETS ACCESS
# -------------------------

def get_secret(key: str, default=None):
    """Safely get a secret from Streamlit secrets."""
    try:
        secrets_dict = dict(st.secrets)
        return secrets_dict.get(key, default)
    except Exception:
        return default


# -------------------------
# LLM COACH HELPER
# -------------------------

def get_ai_coach_reply(prompt_text: str, user_context: dict) -> str:
    """
    Route the AI Career Coach to Anthropic (Claude) or OpenAI (ChatGPT)
    depending on LLM_PROVIDER in Streamlit secrets.
    Falls back to a scripted response if no valid provider/key.
    """

    provider = get_secret("LLM_PROVIDER", "anthropic").lower()
    anthropic_key = get_secret("ANTHROPIC_API_KEY")
    openai_key = get_secret("OPENAI_API_KEY")

    def fallback_reply() -> str:
        strengths = ", ".join(user_context.get("top_strengths", [])) or "your existing strengths"
        career = user_context.get("chosen_direction_label") or user_context.get("direction_label") or "the roles you are exploring"
        main_gap = user_context.get("main_gap") or "one or two key skills"
        horizon = user_context.get("horizon_label", "the next 3–6 months")

        return (
            f"Here is how I would think about {horizon} from here:\n\n"
            f"**1. Anchor in what already works.** {strengths} are not accidents – they are the "
            f"foundation for any career move you make. Design your next steps so they keep showing up.\n\n"
            f"**2. Treat {career} as a hypothesis, not a destiny.** Use the next phase to *test* whether "
            "the work, people, and problems in that direction feel right in practice.\n\n"
            f"**3. Deliberate stretch.** Focus on {main_gap}. Choose one small project, habit, or commitment "
            "you can realistically sustain for 4–6 weeks that directly exercises that skill.\n\n"
            "**4. Make it a shared conversation.** Take this report and your draft plan to a mentor, friend, "
            "or counsellor. Ask them: *What feels true? What feels off? What are we not seeing?*\n\n"
            "The goal is not to find a perfect plan, but to keep taking informed, low-risk steps that teach you "
            "more about what actually fits."
        )

    system_msg = (
        "You are a gentle but honest career coach. You help people turn structured assessments "
        "into a realistic 3–6 month plan. You focus on experiments, conversations, and habits. "
        "You do not promise specific salaries or guaranteed outcomes. You speak clearly and simply."
    )
    
    user_msg = (
        "Here is structured context about the user:\n"
        f"{json.dumps(user_context, indent=2)}\n\n"
        f"Here is what they just wrote:\n{prompt_text}\n\n"
        "Give them: (1) what matters most right now, "
        "(2) how to frame the next 3–6 months, "
        "(3) 1–3 concrete, low-risk experiments they can run. "
        "Keep it under 350 words. Use markdown formatting."
    )

    # Anthropic / Claude
    if provider == "anthropic" and anthropic_key and ANTHROPIC_AVAILABLE:
        try:
            client = anthropic.Anthropic(api_key=anthropic_key)
            messages = [{"role": "user", "content": user_msg}]
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",  # FIXED: use current model
                max_tokens=500,
                temperature=0.5,
                system=system_msg,
                messages=messages,
            )
            return resp.content[0].text.strip()
        except Exception as e:
            st.warning(f"Claude error – using fallback coach. ({e})")
            return fallback_reply()

    # OpenAI / ChatGPT
    if provider == "openai" and openai_key and OPENAI_AVAILABLE:
        try:
            client = OpenAI(api_key=openai_key)  # FIXED: pass key directly
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # FIXED: correct model name
                max_tokens=500,
                temperature=0.6,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            st.warning(f"OpenAI error – using fallback coach. ({e})")
            return fallback_reply()

    # Fallback (no API keys or libraries)
    return fallback_reply()


# -------------------------
# DATA & HELPER FUNCTIONS
# -------------------------

SKILL_GROUPS = {
    "Cognitive": [
        "Problem solving",
        "Learning new things quickly",
        "Analytical thinking",
    ],
    "Technical / Tools": [
        "Working with data or numbers",
        "Using digital tools / software",
        "Building or fixing systems",
    ],
    "People / Communication": [
        "Explaining ideas clearly",
        "Listening and supporting others",
        "Leading or organising people",
    ],
    "Execution / Delivery": [
        "Finishing what you start",
        "Managing your time",
        "Handling pressure or setbacks",
    ],
}

CAREER_OPTIONS = [
    "Product manager",
    "Software developer",
    "Data analyst",
    "UX designer",
    "Marketing specialist",
    "Teacher / educator",
    "Healthcare worker",
    "Policy / public sector",
    "Entrepreneur / founder",
    "Undecided / just exploring",
]


def ensure_data_dir():
    os.makedirs("careercraft_sessions", exist_ok=True)


def save_session(payload: dict):
    try:
        ensure_data_dir()
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        fname = f"careercraft_sessions/session_{ts}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        # Silent failure is fine for now – we do not want to block UX
        pass


def compute_strengths_and_gaps(skill_scores: dict):
    """Compute top strengths and main gap from skill scores."""
    if not skill_scores:
        return [], None

    items = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
    top_strengths = [s for s, v in items[:3] if v >= 55]
    main_gap = items[-1][0] if items[-1][1] <= 45 else None
    return top_strengths, main_gap


def infer_direction(entry_mode: str, career_choice: str, strengths: list):
    """Infer a direction label based on inputs."""
    if career_choice and career_choice != "Undecided / just exploring":
        direction_label = career_choice
    elif strengths:
        direction_label = f"roles that lean on {strengths[0].lower()}"
    else:
        direction_label = "a small set of test roles, not one perfect answer"

    return direction_label


def readiness_band(num_gaps: int):
    """Return readiness label based on number of gaps."""
    if num_gaps <= 1:
        return "Ready"
    elif num_gaps <= 3:
        return "Stretch"
    else:
        return "Long-shot"


# -------------------------
# MAIN UI SECTIONS
# -------------------------

def render_hero():
    st.markdown(
        """
        <div class="hero-card">
          <div class="badge-pill">
            <div class="pill-dot"></div>
            CareerCheck • ~ 7–10 minutes
          </div>
          <div class="hero-title">
            Build a clearer career story before you talk to anyone.
          </div>
          <p class="hero-sub">
            CareerCraft turns your skills and options into a 6–12 month direction, a 3-month phase,
            and a 4–6 week sprint you can take to a mentor, friend, or counsellor.
          </p>
          <div class="hero-grid">
            <div>
              <div class="hero-pill-col-title">You will leave with</div>
              <div class="hero-pill-col-body">
                • A short list of directions that fit you<br/>
                • The next 3 months framed as a clear phase<br/>
                • A simple 4–6 week experiment plan
              </div>
            </div>
            <div>
              <div class="hero-pill-col-title">How CareerCraft is different</div>
              <div class="hero-pill-col-body">
                Not a magic quiz. Not a chatbot pretending to know your destiny.
                A structured pre-conversation layer that makes mentoring, coaching,
                and self-reflection more concrete.
              </div>
            </div>
            <div>
              <div class="hero-pill-col-title">Designed for</div>
              <div class="hero-pill-col-body">
                Students, early-career professionals, career-changers, and the mentors
                who back them.
              </div>
            </div>
          </div>
          <div class="hero-footnote">
            This is decision support, not prophecy. Use it as a conversation starter, not a verdict.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_entry_cards():
    st.markdown(
        """
        <div class="entry-row">
          <div class="entry-card">
            <div class="entry-pill-label">Path A</div>
            <div class="entry-title">Start from my skills</div>
            <div class="entry-body">
              Map what you are already good at across cognitive, technical, people, and execution skills.
              We will suggest directions that make the most of what is already working.
            </div>
            <div class="entry-cta">Choose this if you feel more clear on who you are than where you are going.</div>
            <div class="entry-emoji left">🎯</div>
          </div>
          <div class="entry-card">
            <div class="entry-pill-label">Path B</div>
            <div class="entry-title">Start from a career</div>
            <div class="entry-body">
              Pick a role (or a few) you are curious about. We will check how close you are,
              where the gaps are, and how to test it without burning everything down.
            </div>
            <div class="entry-cta">Choose this if you have some directions in mind, even loosely.</div>
            <div class="entry-emoji right">🧭</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")  # spacing

    cols = st.columns(2)
    with cols[0]:
        if st.button("🎯 Start from my skills →", use_container_width=True, type="primary"):
            st.session_state["started"] = True
            st.session_state["entry_mode"] = "skills"
            st.rerun()
    with cols[1]:
        if st.button("🧭 Start from a career →", use_container_width=True, type="primary"):
            st.session_state["started"] = True
            st.session_state["entry_mode"] = "career"
            st.rerun()


def render_skills_flow():
    st.markdown('<div class="section-title">Step 1 · Map your skills</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Rate how often each statement feels true in your current real life.</div>',
        unsafe_allow_html=True,
    )

    skill_scores = {}
    for group, skills in SKILL_GROUPS.items():
        st.markdown(f"**{group}**")
        for skill in skills:
            val = st.slider(
                skill,
                min_value=0,
                max_value=100,
                value=60,
                step=10,
                help="0 = almost never, 100 = this shows up most weeks",
                key=f"skill_{skill}",
            )
            skill_scores[skill] = val
        st.write("")

    curious_role = st.text_input(
        "If there is a role or direction you are curious about, write it here (optional):",
        placeholder="e.g. Product management in tech, community health, social impact consulting…",
        key="curious_role_input",
    )

    st.write("")
    if st.button("Generate my CareerCheck →", type="primary", use_container_width=True):
        st.session_state["skill_scores"] = skill_scores
        st.session_state["curious_role"] = curious_role
        st.session_state["flow_done"] = True
        st.rerun()


def render_career_flow():
    st.markdown('<div class="section-title">Step 1 · Choose the directions you want to test</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">You can always change your mind later. This is about testing hypotheses, not locking in forever.</div>',
        unsafe_allow_html=True,
    )

    current = st.selectbox(
        "Your current situation",
        ["Student", "Working in a job", "Between roles", "Something else / mixed"],
        key="career_current_select",
    )
    target = st.multiselect(
        "Roles or directions you are considering",
        options=CAREER_OPTIONS,
        default=["Undecided / just exploring"],
        help="Pick 1–3 that feel relevant, even if you are not sure.",
        key="career_target_select",
    )

    st.markdown("**Quick sense check – how do these feel right now?**")
    col1, col2, col3 = st.columns(3)
    with col1:
        pull = st.slider("How strong is the pull towards these directions?", 0, 100, 70, 10, key="pull_slider")
    with col2:
        risk = st.slider("How risky would a move feel right now?", 0, 100, 50, 10, key="risk_slider")
    with col3:
        energy = st.slider("How much energy do you have for career changes?", 0, 100, 60, 10, key="energy_slider")

    st.write("")
    if st.button("Generate my CareerCheck →", type="primary", use_container_width=True):
        st.session_state["career_current"] = current
        st.session_state["career_targets"] = target
        st.session_state["career_pulls"] = {"pull": pull, "risk": risk, "energy": energy}
        st.session_state["flow_done"] = True
        st.rerun()


def render_results_and_coach(entry_mode: str):
    st.markdown('<div class="section-title">Step 2 · Directions from here</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">These are not predictions. They are starting points for better conversations.</div>',
        unsafe_allow_html=True,
    )

    if entry_mode == "skills":
        skill_scores = st.session_state.get("skill_scores", {})
        curious_role = st.session_state.get("curious_role", "").strip()
        strengths, gap = compute_strengths_and_gaps(skill_scores)
        direction_label = infer_direction(entry_mode, curious_role, strengths)
        num_gaps = len([s for s, v in skill_scores.items() if v <= 50])
    else:
        skill_scores = {}
        strengths, gap = [], None
        targets = st.session_state.get("career_targets", [])
        direction_label = ", ".join(targets) if targets else "a few test directions"
        pulls = st.session_state.get("career_pulls", {})
        num_gaps = 2 if pulls.get("risk", 50) > 60 else 1

    readiness = readiness_band(num_gaps)
    horizon_label = "the next 3–6 months"

    # Directions cards (deeper / lateral / stretch)
    col_left, col_right = st.columns([1.1, 1.1])
    with col_left:
        st.markdown("**Career directions**")
        # Deeper
        st.markdown(
            f"""
            <div class="direction-card">
              <div class="direction-header">
                Go deeper in this lane
                <span class="pill-readiness">{readiness}</span>
              </div>
              <div class="direction-meta">
                Anchored in: {direction_label}
              </div>
              <div class="direction-body">
                Double down where you already have traction. Look for ways to increase scope, complexity
                or responsibility without completely changing environment.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Lateral
        st.markdown(
            """
            <div class="direction-card lateral">
              <div class="direction-header">
                Explore a lateral move
              </div>
              <div class="direction-meta">
                Keep your strengths, change the context
              </div>
              <div class="direction-body">
                Identify roles that use a similar skill mix in a different team, industry, or organisation type.
                Think of this as "same muscles, new arena".
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Stretch
        st.markdown(
            """
            <div class="direction-card stretch">
              <div class="direction-header">
                Design one stretch experiment
                <span class="pill-readiness stretch">Stretch</span>
              </div>
              <div class="direction-meta">
                4–6 week, low-risk test
              </div>
              <div class="direction-body">
                Choose a project, course, or commitment that feels slightly uncomfortable but not catastrophic.
                The goal is to learn about fit, not to prove yourself once and for all.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Sprint + Coach
    with col_right:
        # Sprint box
        sprint_focus = gap or "one focused skill or habit"
        st.markdown(
            f"""
            <div class="sprint-box">
              <div class="sprint-tag">4–6 week sprint</div>
              <div class="sprint-title">Make {sprint_focus.lower()} the centre of gravity.</div>
              <div class="sprint-body">
                Pick one anchor activity that directly exercises this: a small project at work,
                a side project, a course with assignments, or a volunteer role. Protect
                2–4 hours a week for it. At the end of the sprint, review: what felt alive,
                what drained you, and what you want more or less of.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.markdown(
            """
            <div class="coach-box">
              <div class="coach-title">💬 AI Career Coach</div>
              <div class="coach-caption">
                Use this to shape what you want to talk about with a mentor, friend, or counsellor.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        user_note = st.text_area(
            "Before you talk to someone, what feels most important, unclear, or scary about your career right now?",
            placeholder="Write a few sentences. This is just for you and the coach.",
            key="coach_input",
        )
        
        if st.button("Ask the Career Coach →", use_container_width=True, type="primary"):
            if user_note.strip():
                context = {
                    "entry_mode": entry_mode,
                    "direction_label": direction_label,
                    "top_strengths": strengths,
                    "main_gap": gap,
                    "horizon_label": horizon_label,
                }
                with st.spinner("Thinking..."):
                    coach_reply = get_ai_coach_reply(user_note, context)
                st.session_state["coach_reply"] = coach_reply
                st.rerun()
            else:
                st.warning("Please write something first so the coach can help.")

        # Display coach reply if exists
        coach_reply = st.session_state.get("coach_reply", "")
        if coach_reply:
            st.markdown(f'<div class="coach-box coach-reply">{coach_reply}</div>', unsafe_allow_html=True)

    # Summary + export
    st.markdown("---")
    st.markdown('<div class="section-title">Step 3 · Turn this into a conversation</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-caption">
          Share this summary with someone you trust. The goal is not to defend the result, but to ask:
          <em>What feels true? What feels off? What are we missing?</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary_cols = st.columns(3)
    with summary_cols[0]:
        st.markdown("**6–12 month direction**")
        st.write(direction_label)
    with summary_cols[1]:
        st.markdown("**3-month phase**")
        st.write("Stabilise your base, then deliberately test one or two adjacent directions.")
    with summary_cols[2]:
        st.markdown("**4–6 week sprint**")
        st.write(f"Design a sprint around {gap or 'one focused skill or habit'} and review at the end.")

    st.write("")
    convo_text = (
        "Here is how I am currently thinking about my career, using CareerCraft:\n\n"
        f"- **Direction (6–12 months):** {direction_label}\n"
        "- **Next 3 months:** Stabilise my base and deliberately test 1–2 adjacent directions.\n"
        f"- **4–6 week sprint focus:** {gap or 'one focused skill or habit'}\n\n"
        "I would love to talk this through with you – what feels true, what feels off, and what "
        "we might be missing."
    )
    st.text_area("Copy this into an email or message to a mentor/friend:", value=convo_text, height=150, key="export_text")

    # Simple external search suggestions
    st.markdown("**Optional – find local courses or events**")
    query = st.text_input(
        "What would you like to search for near you?",
        placeholder="e.g. beginner product management course Melbourne, data meetups Sydney…",
        key="search_query",
    )
    if query:
        st.markdown(
            f"- [Search Eventbrite](https://www.eventbrite.com.au/d/online/{query.replace(' ', '-')}/)\n"
            f"- [Search LinkedIn Learning](https://www.linkedin.com/learning/search?keywords={query.replace(' ', '%20')})\n"
            f"- [Search Google](https://www.google.com/search?q={query.replace(' ', '+')})",
            unsafe_allow_html=False,
        )

    # Save minimal session data
    payload = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "entry_mode": entry_mode,
        "skill_scores": st.session_state.get("skill_scores"),
        "curious_role": st.session_state.get("curious_role"),
        "career_current": st.session_state.get("career_current"),
        "career_targets": st.session_state.get("career_targets"),
        "career_pulls": st.session_state.get("career_pulls"),
        "direction_label": direction_label,
        "strengths": strengths,
        "gap": gap,
        "coach_reply": st.session_state.get("coach_reply"),
    }
    save_session(payload)

    # Reset button
    st.markdown("---")
    if st.button("Start a new CareerCheck", use_container_width=True):
        for key in ["started", "entry_mode", "flow_done", "skill_scores", "curious_role", 
                    "career_current", "career_targets", "career_pulls", "coach_reply"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


# -------------------------
# APP ENTRYPOINT
# -------------------------

def main():
    # Initialize session state
    if "started" not in st.session_state:
        st.session_state["started"] = False
    if "flow_done" not in st.session_state:
        st.session_state["flow_done"] = False

    # Always show hero
    render_hero()
    
    st.write("")

    # If not started, show entry cards
    if not st.session_state["started"]:
        render_entry_cards()
    else:
        # Started - check entry mode
        entry_mode = st.session_state.get("entry_mode")
        
        if not entry_mode:
            # Should not happen, but handle gracefully
            render_entry_cards()
        elif not st.session_state["flow_done"]:
            # Show the appropriate flow
            st.markdown("---")
            if entry_mode == "skills":
                render_skills_flow()
            else:
                render_career_flow()
        else:
            # Show results
            st.markdown("---")
            render_results_and_coach(entry_mode)


if __name__ == "__main__":
    main()
