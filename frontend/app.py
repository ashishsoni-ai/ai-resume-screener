"""
Streamlit Frontend — AI Resume Screener

Connects to the FastAPI backend at BACKEND_URL.
Set BACKEND_URL in .env or as environment variable.
"""
import os
import json
import requests
import streamlit as st
# from dotenv import load_dotenv

# load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — clean modern look
# ─────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .score-number {
        font-size: 4rem;
        font-weight: 800;
        line-height: 1;
    }
    .level-badge {
        font-size: 1.2rem;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .skill-bar-label {
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #4a4a4a;
        border-left: 4px solid #667eea;
        padding-left: 0.75rem;
        margin: 1.5rem 0 0.75rem 0;
    }
    .tag {
        display: inline-block;
        background: #f0f0ff;
        color: #4a3f8f;
        border: 1px solid #d0c8ff;
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        margin: 0.2rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .hire-yes { color: #16a34a; font-weight: 700; font-size: 1.1rem; }
    .hire-maybe { color: #ca8a04; font-weight: 700; font-size: 1.1rem; }
    .hire-no { color: #dc2626; font-weight: 700; font-size: 1.1rem; }
    .stProgress .st-bo { background-color: #667eea; }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR — History
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("## 📋 Past Screenings")
        try:
            res = requests.get(f"{BACKEND_URL}/api/history", timeout=5)
            if res.ok:
                sessions = res.json().get("sessions", [])
                if not sessions:
                    st.caption("No past screenings yet.")
                for s in sessions[:10]:
                    name = s.get("candidate_name") or "Unknown"
                    score = s.get("final_score") or "—"
                    level = s.get("level") or ""
                    if st.button(f"🎯 {name} — {score}/100 ({level})", key=s["session_id"]):
                        st.session_state["view_session"] = s["session_id"]
                        st.rerun()
        except Exception:
            st.caption("Backend not reachable.")

        st.divider()
        st.caption("Built with LangGraph + Groq")
        st.caption("github.com/ashishsoni-ai")


# ─────────────────────────────────────────────
# SKILL DIMENSION RENDERER
# ─────────────────────────────────────────────

def render_skill_bars(skill_analysis: dict):
    dimensions = [
        ("python", "🐍 Python"),
        ("machine_learning", "🧠 Machine Learning"),
        ("llm_genai", "🤖 LLM / GenAI"),
        ("backend_engineering", "⚙️ Backend Engineering"),
        ("project_complexity", "🏗️ Project Complexity"),
    ]
    for key, label in dimensions:
        dim = skill_analysis.get(key, {})
        score = dim.get("score", 0)
        evidence = dim.get("evidence", "")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<div class="skill-bar-label">{label}</div>', unsafe_allow_html=True)
            st.progress(score / 10)
            if evidence:
                st.caption(evidence)
        with col2:
            st.markdown(f"### {score}/10")


# ─────────────────────────────────────────────
# FULL RESULT RENDERER
# ─────────────────────────────────────────────

def render_results(result: dict):
    extracted = result.get("extracted_info", {})
    skill_analysis = result.get("skill_analysis", {})
    score_data = result.get("candidate_score", {})
    report_md = result.get("report_markdown", "")

    candidate_name = result.get("candidate_name") or extracted.get("name") or "Candidate"
    final_score = score_data.get("final_score", 0)
    level = score_data.get("level", "—")
    hire_rec = score_data.get("hire_recommendation", "—")
    summary = score_data.get("summary", "")

    # ── Score Card ──
    st.markdown(f"""
    <div class="score-card">
        <div style="font-size:1.4rem; margin-bottom:0.5rem;">🎯 {candidate_name}</div>
        <div class="score-number">{final_score}</div>
        <div style="font-size:1rem; margin: 0.25rem 0;">/ 100</div>
        <div class="level-badge">{level}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary + Hire Rec ──
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"📝 {summary}")
    with col_b:
        hire_color = "hire-yes" if "Yes" in hire_rec else ("hire-maybe" if "Maybe" in hire_rec else "hire-no")
        st.markdown(f"**Hire Recommendation:**")
        st.markdown(f'<div class="{hire_color}">{hire_rec}</div>', unsafe_allow_html=True)

    st.divider()

    # ── Two-column layout ──
    left, right = st.columns(2)

    with left:
        # Skill Analysis
        st.markdown('<div class="section-header">🔬 Skill Analysis</div>', unsafe_allow_html=True)
        render_skill_bars(skill_analysis)
        overall = skill_analysis.get("overall_reasoning", "")
        if overall:
            st.caption(f"💬 {overall}")

        # Skills
        skills = extracted.get("skills", {})
        all_skills = []
        for category_skills in skills.values():
            if isinstance(category_skills, list):
                all_skills.extend(category_skills)
        if all_skills:
            st.markdown('<div class="section-header">🛠️ Skills</div>', unsafe_allow_html=True)
            tags_html = " ".join([f'<span class="tag">{s}</span>' for s in all_skills])
            st.markdown(tags_html, unsafe_allow_html=True)

        # Strengths & Gaps
        strengths = score_data.get("strengths", [])
        gaps = score_data.get("gaps", [])
        if strengths:
            st.markdown('<div class="section-header">✅ Strengths</div>', unsafe_allow_html=True)
            for s in strengths:
                st.markdown(f"- {s}")
        if gaps:
            st.markdown('<div class="section-header">⚠️ Gaps</div>', unsafe_allow_html=True)
            for g in gaps:
                st.markdown(f"- {g}")

    with right:
        # Projects
        projects = extracted.get("projects", [])
        if projects:
            st.markdown('<div class="section-header">🏗️ Projects</div>', unsafe_allow_html=True)
            for proj in projects:
                with st.expander(f"📌 {proj.get('name', 'Project')}"):
                    st.write(proj.get("description", ""))
                    techs = proj.get("technologies", [])
                    if techs:
                        st.markdown(" ".join([f'<span class="tag">{t}</span>' for t in techs]), unsafe_allow_html=True)
                    highlight = proj.get("highlights", "")
                    if highlight:
                        st.success(f"⭐ {highlight}")

        # Interview Questions
        questions = score_data.get("suggested_interview_questions", [])
        if questions:
            st.markdown('<div class="section-header">❓ Interview Questions</div>', unsafe_allow_html=True)
            for i, q in enumerate(questions, 1):
                st.markdown(f"**{i}.** {q}")

        # Resume Tips
        tips = score_data.get("resume_improvement_tips", [])
        if tips:
            st.markdown('<div class="section-header">💡 Resume Tips</div>', unsafe_allow_html=True)
            for tip in tips:
                st.markdown(f"- {tip}")

    st.divider()

    # ── Full Report Tab ──
    with st.expander("📄 Full Recruiter Report (Markdown)", expanded=False):
        st.markdown(report_md)

    with st.expander("🔎 Raw Extracted Data (JSON)", expanded=False):
        st.json(extracted)


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────

def main():
    render_sidebar()

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI Resume Screener</h1>
        <p style="color:#666; font-size:1.1rem;">
            Multi-agent LangGraph pipeline · Groq LLM · Instant tech proficiency scoring
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Check if viewing a past session
    if "view_session" in st.session_state:
        session_id = st.session_state.pop("view_session")
        try:
            res = requests.get(f"{BACKEND_URL}/api/session/{session_id}", timeout=10)
            if res.ok:
                data = res.json()
                st.success(f"📂 Loaded session: {session_id}")
                result = {
                    "candidate_name": data.get("candidate_name"),
                    "extracted_info": data.get("extracted_info", {}),
                    "skill_analysis": data.get("skill_analysis", {}),
                    "candidate_score": data.get("candidate_score", {}),
                    "report_markdown": data.get("report_markdown", ""),
                }
                render_results(result)
                return
        except Exception as e:
            st.error(f"Could not load session: {e}")

    # Upload section
    st.markdown("### 📤 Upload Resume")
    uploaded_file = st.file_uploader(
        "Drop a PDF or DOCX file",
        type=["pdf", "docx", "doc"],
        help="Max 5MB. PDF or DOCX format.",
    )

    if uploaded_file:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            screen_btn = st.button("🚀 Screen Resume", use_container_width=True, type="primary")

        if screen_btn:
            with st.spinner("🤖 Running 4-agent pipeline... (15-30 seconds)"):
                # Progress simulation for UX
                progress = st.progress(0, text="📄 Parsing resume...")
                import time

                try:
                    res = requests.post(
                        f"{BACKEND_URL}/api/screen",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        timeout=120,
                    )

                    progress.progress(25, text="🔍 Extracting information...")
                    time.sleep(0.5)
                    progress.progress(50, text="🧠 Analyzing skills...")
                    time.sleep(0.5)
                    progress.progress(75, text="🎯 Generating score...")
                    time.sleep(0.5)
                    progress.progress(100, text="📝 Building report...")
                    time.sleep(0.3)
                    progress.empty()

                    if res.ok:
                        data = res.json()
                        st.success("✅ Screening complete!")
                        render_results(data["result"])
                    else:
                        err = res.json().get("detail", "Unknown error")
                        st.error(f"❌ Screening failed: {err}")

                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The pipeline is taking too long.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
