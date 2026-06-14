import streamlit as st
import tempfile
import os
import json
from dotenv import load_dotenv

load_dotenv()

from ingest import ingest_pdf, ingest_text
from generate import generate_report

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobSense — AI Career Coach",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ── Reset & base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #F8F9FB !important;
    color: #1A1D23;
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #F8F9FB !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hide deploy/preview toolbar (Empty · Inputs filled · Full report) ── */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stDeployButton"],
.stDeployButton,
div[class*="toolbar"],
div[class*="Toolbar"],
iframe[title="streamlit_analytics"] { display: none !important; }

/* ── Typography ── */
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

/* ── Top nav bar ── */
.topnav {
    background: #fff;
    border-bottom: 1px solid #E8ECF0;
    padding: 0 2.5rem;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.topnav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 17px;
    color: #1A1D23;
}
.topnav-logo-icon {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
}
.topnav-logo-sub {
    font-size: 12px;
    color: #94A3B8;
    font-weight: 400;
    font-family: 'Inter', sans-serif;
    margin-left: 2px;
}
.topnav-right {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 13px;
}
.topnav-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #64748B;
    font-weight: 500;
}
.topnav-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #10B981;
    display: inline-block;
}
.topnav-github {
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 5px 14px;
    font-size: 14px;
    color: black;
    font-weight: 500;
    cursor: pointer;
    
}
    .topnav-github a{
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 5px 14px;
    font-size: 14px;
    color: black;
    font-weight: 500;
    cursor: pointer;
    underline: none;
            text-decoration: none;
}

/* ── Hero section ── */
.hero {
    text-align: center;
    padding: 3.5rem 1rem 2.5rem;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #F1F0FF;
    border: 1px solid #DDD9FF;
    border-radius: 20px;
    padding: 5px 16px;
    font-size: 11.5px;
    font-weight: 600;
    color: #6366F1;
    letter-spacing: .06em;
    text-transform: uppercase;
    margin-bottom: 1.4rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    line-height: 1.18;
    color: #0F172A;
    margin-bottom: .6rem;
    letter-spacing: -.02em;
}
.hero-title span {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.05rem;
    color: #64748B;
    max-width: 520px;
    margin: 0 auto 1.8rem;
    line-height: 1.65;
    font-weight: 400;
}
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    flex-wrap: wrap;
}
.hero-stat {
    font-size: 12px;
    color: #94A3B8;
    display: flex;
    align-items: center;
    gap: 5px;
    font-weight: 500;
}

/* ── Input section wrapper ── */
.input-section {
    background: #fff;
    border: 1px solid #E8ECF0;
    border-radius: 20px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
}

/* ── Input labels ── */
.input-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: #0F172A;
    text-transform: uppercase;
    letter-spacing: .06em;
    margin-bottom: .8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Streamlit widget overrides ── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed #C8D3E0 !important;
    border-radius: 14px !important;
    background: #ffffff !important;
    transition: border-color .2s !important;
}
[data-testid="stFileUploader"] > div {
    background: #ffffff !important;
    border-radius: 14px !important;
}
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border-radius: 14px !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #6366F1 !important;
}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p { color: #374151 !important; font-size: 14px !important; }
[data-testid="stFileUploader"] small { color: #94A3B8 !important; font-size: 12px !important; }
[data-testid="stFileUploaderDropzoneInstructions"] { background: #fff !important; }
[data-testid="stFileUploaderDropzoneInstructions"] div { background: #fff !important; }

[data-testid="stTextArea"] textarea {
    background: #FAFBFC !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 14px !important;
    color: #1A1D23 !important;
    font-size: 13.5px !important;
    font-family: 'Inter', sans-serif !important;
    resize: none !important;
    transition: border-color .2s !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.10) !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: #C1C9D4 !important; }

/* ── Primary button ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 14px 28px !important;
    letter-spacing: .01em !important;
    box-shadow: 0 4px 20px rgba(99,102,241,.25) !important;
    transition: all .2s !important;
    width: 100% !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,.35) !important;
}
[data-testid="stButton"] > button[kind="secondary"] {
    background: #fff !important;
    color: #64748B !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 14px !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    transition: all .2s !important;
    width: 100% !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    color: #1A1D23 !important;
    border-color: #B0BAC9 !important;
    background: #F8F9FB !important;
}

/* ── Score ring ── */
.score-section {
    background: #fff;
    border: 1px solid #E8ECF0;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.score-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 4.5rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: .3rem;
}
.score-label {
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: #94A3B8;
    margin-bottom: .8rem;
}
.score-verdict {
    font-size: 14px;
    color: #64748B;
    font-weight: 500;
    margin-top: .5rem;
}

/* ── Report cards ── */
.report-card {
    background: #fff;
    border: 1px solid #E8ECF0;
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,.03);
    position: relative;
    overflow: hidden;
}
.report-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 3px 0 0 3px;
}
.card-green::before  { background: #10B981; }
.card-red::before    { background: #EF4444; }
.card-blue::before   { background: #6366F1; }
.card-yellow::before { background: #F59E0B; }
.card-purple::before { background: #8B5CF6; }

.card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .09em;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 7px;
}
.card-green .card-title  { color: #059669; }
.card-red .card-title    { color: #DC2626; }
.card-blue .card-title   { color: #6366F1; }
.card-yellow .card-title { color: #D97706; }
.card-purple .card-title { color: #7C3AED; }

.skill-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 500;
    margin: 3px;
}
.chip-green { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
.chip-red   { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }

.point-item {
    display: flex;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #F1F5F9;
    font-size: 13.5px;
    color: #475569;
    line-height: 1.55;
    align-items: flex-start;
}
.point-item:last-child { border-bottom: none; padding-bottom: 0; }
.point-num {
    width: 22px; height: 22px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}
.num-yellow { background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }
.num-purple { background: #F5F3FF; color: #7C3AED; border: 1px solid #DDD6FE; }

.bullet-item {
    background: #F8F9FB;
    border: 1px solid #E8ECF0;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #374151;
    line-height: 1.6;
    font-family: 'Inter', sans-serif;
    position: relative;
}
.copy-hint {
    font-size: 10px;
    color: #CBD5E1;
    position: absolute;
    top: 8px; right: 12px;
    font-weight: 500;
}

/* ── Progress bar ── */
.progress-track {
    background: #E8ECF0;
    border-radius: 99px;
    height: 8px;
    overflow: hidden;
    margin: .8rem 0;
}
.progress-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 1s ease;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #fff !important;
    color: #6366F1 !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all .2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #F5F3FF !important;
    border-color: #6366F1 !important;
}

/* ── Status widget ── */
[data-testid="stStatusWidget"] {
    background: #fff !important;
    border: 1px solid #E8ECF0 !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.04) !important;
}

/* ── Divider ── */
hr { border-color: #E8ECF0 !important; margin: 1.8rem 0 !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: #fff !important;
    border-radius: 10px !important;
    border: 1px solid #E8ECF0 !important;
    color: #374151 !important;
}

/* ── Column gap ── */
[data-testid="column"] { padding: 0 8px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #F8F9FB; }
::-webkit-scrollbar-thumb { background: #E2E8F0; border-radius: 99px; }

/* ── Upload success tag ── */
.upload-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 12px;
    color: #059669;
    margin-top: 8px;
    font-weight: 600;
}

/* ── Word count ── */
.word-count {
    font-size: 11px;
    text-align: right;
    margin-top: 4px;
    font-weight: 500;
}

/* ── Section label ── */
.section-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: #94A3B8;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #E8ECF0;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #94A3B8;
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: .4; }
.empty-text { font-size: 15px; color: #64748B; margin-bottom: .4rem; font-weight: 500; }
.empty-sub  { font-size: 13px; color: #94A3B8; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .hero-title { font-size: 1.8rem; }
    .hero-stats { gap: 1rem; }
    .score-number { font-size: 3.5rem; }
    .topnav { padding: 0 1rem; }
}
</style>
""", unsafe_allow_html=True)


# ── Top Nav ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topnav">
    <div class="topnav-logo">
        <div class="topnav-logo-icon">🧠</div>
        <div>
            JobSense
            <div class="topnav-logo-sub">AI Career Coach</div>
        </div>
    </div>
    <div class="topnav-right">
        <div class="topnav-badge">
            <span class="topnav-dot"></span>
            100% free · no login
        </div>
        <div class="topnav-github"><a href="https://github.com/groq/jobsense" target="_blank">⭐ GitHub</a></div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge"></div>
    <div class="hero-title">Know your odds before<br>you <span>hit send</span></div>
    <div class="hero-sub">Upload your CV, paste any job description — get a match score, gap analysis, and tailored interview prep in seconds.</div>
    <div class="hero-stats">
        <div class="hero-stat">⚡ ~8 sec analysis</div>
        <div class="hero-stat">🔒 Data stays local</div>
        <div class="hero-stat">🧠 Llama 3.3 70B</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Input section ─────────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="input-label">📄 &nbsp;Your CV</div>', unsafe_allow_html=True)
        cv_file = st.file_uploader(
            "cv_upload",
            type="pdf",
            label_visibility="collapsed",
            help="Text-based PDF only. Scanned/image PDFs won't extract correctly."
        )
        if cv_file:
            st.markdown(f'<div class="upload-tag">✓ &nbsp;{cv_file.name}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="input-label">💼 &nbsp;Job Description</div>', unsafe_allow_html=True)
        jd_text = st.text_area(
            "jd_input",
            height=180,
            placeholder="Paste the full job description here...\n\nFrom LinkedIn, Rozee.pk, Indeed — anywhere.\nMore text = sharper analysis.",
            label_visibility="collapsed"
        )
        if jd_text:
            wc = len(jd_text.split())
            color = "#059669" if wc >= 80 else "#D97706" if wc >= 30 else "#DC2626"
            st.markdown(f'<div class="word-count" style="color:{color}">{wc} words {"✓" if wc >= 80 else "— add more for better results"}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── Buttons ───────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
b1, b2 = st.columns([5, 1], gap="small")
with b1:
    analyse = st.button("🔍  Analyse my application", type="primary", use_container_width=True)
with b2:
    clear = st.button("Clear", type="secondary", use_container_width=True)


# ── Clear ─────────────────────────────────────────────────────────────────────
if clear:
    st.session_state.clear()
    st.rerun()


# ── Analysis ─────────────────────────────────────────────────────────────────
if analyse:
    if not cv_file:
        st.error("Upload your CV as a PDF to continue.")
        st.stop()
    if not jd_text.strip():
        st.error("Paste the job description to continue.")
        st.stop()
    if len(jd_text.split()) < 20:
        st.warning("Job description looks too short — paste the full text for an accurate analysis.")

    try:
        with st.status("Working on your report...", expanded=True) as status:
            st.write("📖 &nbsp;Reading and embedding your CV...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                f.write(cv_file.read())
                tmp = f.name
            cv_store = ingest_pdf(tmp)
            os.unlink(tmp)

            st.write("💼 &nbsp;Reading and embedding job description...")
            jd_store = ingest_text(jd_text)

            st.write("🤖 &nbsp;Llama 3.3 70B is analysing the match...")
            report = generate_report(cv_store, jd_store)
            st.session_state.report = report

            status.update(label="✅ &nbsp;Report ready!", state="complete", expanded=False)

    except ValueError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")
        st.caption("Check your GROQ_API_KEY in .env and try again.")
        st.stop()


# ── Report ────────────────────────────────────────────────────────────────────
if "report" in st.session_state:
    r = st.session_state.report

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Your results</div>', unsafe_allow_html=True)

    # Score + skills row
    score_col, skills_col = st.columns([1, 2], gap="medium")

    with score_col:
        score = r.get("match_score", 0)
        if score >= 70:
            score_color = "#10B981"
            verdict = "Strong match"
            emoji = "🟢"
        elif score >= 50:
            score_color = "#F59E0B"
            verdict = "Worth applying"
            emoji = "🟡"
        else:
            score_color = "#EF4444"
            verdict = "Significant gaps"
            emoji = "🔴"

        st.markdown(f"""
        <div class="score-section">
            <div class="score-label">Match Score</div>
            <div class="score-number" style="color:{score_color}">{score}%</div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{score}%;background:{score_color}"></div>
            </div>
            <div class="score-verdict">{emoji} &nbsp;{verdict}</div>
        </div>
        """, unsafe_allow_html=True)

    with skills_col:
        matched = r.get("matched_skills", [])
        chips_green = "".join(f'<span class="skill-chip chip-green">✓ {s}</span>' for s in matched) or "<span style='color:#94A3B8;font-size:13px'>None identified</span>"
        st.markdown(f"""
        <div class="report-card card-green">
            <div class="card-title">✅ &nbsp;Skills you already have</div>
            <div>{chips_green}</div>
        </div>
        """, unsafe_allow_html=True)

        missing = r.get("missing_skills", [])
        chips_red = "".join(f'<span class="skill-chip chip-red">✗ {s}</span>' for s in missing) or "<span style='color:#94A3B8;font-size:13px'>No major gaps!</span>"
        st.markdown(f"""
        <div class="report-card card-red">
            <div class="card-title">❌ &nbsp;Skills to develop</div>
            <div>{chips_red}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Strengths + Talking points
    left_col, right_col = st.columns(2, gap="medium")

    with left_col:
        strengths = r.get("strengths", [])
        items = "".join(f'<div class="point-item"><div class="point-num num-purple">💪</div><div>{s}</div></div>' for s in strengths)
        st.markdown(f"""
        <div class="report-card card-purple">
            <div class="card-title">💪 &nbsp;Strengths to highlight</div>
            {items}
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        points = r.get("interview_talking_points", [])
        items = "".join(f'<div class="point-item"><div class="point-num num-yellow">{i+1}</div><div>{p}</div></div>' for i, p in enumerate(points))
        st.markdown(f"""
        <div class="report-card card-yellow">
            <div class="card-title">💬 &nbsp;Interview talking points</div>
            {items}
        </div>
        """, unsafe_allow_html=True)

    # Rewritten CV bullets
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Rewritten CV bullets — tailored to this job</div>', unsafe_allow_html=True)

    bullets = r.get("rewritten_bullets", [])
    bullets_html = "".join(f"""
    <div class="bullet-item">
        <span class="copy-hint">click to copy</span>
        {b}
    </div>""" for b in bullets)

    st.markdown(f'<div class="report-card card-blue"><div class="card-title">✍️ &nbsp;Drop these directly into your CV</div>{bullets_html}</div>', unsafe_allow_html=True)

    # Download + new analysis
    st.markdown("<br>", unsafe_allow_html=True)
    dl1, dl2, dl3 = st.columns([1, 1, 2])
    with dl1:
        st.download_button(
            "⬇️ Download report",
            data=json.dumps(r, indent=2),
            file_name="jobsense_report.json",
            mime="application/json",
            use_container_width=True
        )
    with dl2:
        if st.button("🔄 New analysis", use_container_width=True):
            st.session_state.clear()
            st.rerun()


# ── Empty state ───────────────────────────────────────────────────────────────
elif not analyse:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🧠</div>
        <div class="empty-text">Your report will appear here</div>
        <div class="empty-sub">Upload your CV and paste a job description above, then hit Analyse</div>
    </div>
    """, unsafe_allow_html=True)