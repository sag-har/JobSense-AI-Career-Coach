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

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stButton > button { width: 100%; }
    .stCodeBlock { font-size: 13px; }
    div[data-testid="metric-container"] {
        background: #1a1a2e;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧠 JobSense — AI Career Coach")
st.caption("Upload your CV + paste a job description → instant gap analysis · powered by **Groq + FAISS + LangChain** · 100% free")
st.divider()


# ── Input section ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your CV")
    cv_file = st.file_uploader(
        "Upload as PDF",
        type="pdf",
        help="Text-based PDFs only. Scanned/image PDFs won't work."
    )
    if cv_file:
        st.success(f"✅ Uploaded: {cv_file.name}")

with col2:
    st.subheader("💼 Job Description")
    jd_text = st.text_area(
        "Paste the full job description",
        height=200,
        placeholder="Paste from LinkedIn, Rozee.pk, Indeed, anywhere...\n\nThe more complete the JD, the better the analysis."
    )
    if jd_text:
        word_count = len(jd_text.split())
        st.caption(f"{word_count} words")


# ── Action buttons ────────────────────────────────────────────────────────────
st.divider()
btn_col, clear_col = st.columns([4, 1])

with btn_col:
    analyse = st.button(
        "🔍 Analyse my application",
        type="primary",
        use_container_width=True
    )

with clear_col:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# ── Validation + Analysis ─────────────────────────────────────────────────────
if analyse:
    if not cv_file:
        st.error("❌ Please upload your CV as a PDF.")
        st.stop()

    if not jd_text.strip():
        st.error("❌ Please paste the job description.")
        st.stop()

    if len(jd_text.split()) < 30:
        st.warning("⚠️ Job description looks too short. Paste the full JD for best results.")

    try:
        with st.status("Analysing your application...", expanded=True) as status:

            st.write("📖 Reading and embedding your CV...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                f.write(cv_file.read())
                tmp_path = f.name
            cv_store = ingest_pdf(tmp_path)
            os.unlink(tmp_path)
            st.write("✅ CV processed.")

            st.write("💼 Reading and embedding job description...")
            jd_store = ingest_text(jd_text)
            st.write("✅ Job description processed.")

            st.write("🤖 Groq (Llama 3.3 70B) is generating your report...")
            report = generate_report(cv_store, jd_store)
            st.session_state.report = report

            status.update(label="✅ Report ready!", state="complete", expanded=False)

    except ValueError as e:
        st.error(f"❌ {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Something went wrong: {str(e)}")
        st.caption("Check your GROQ_API_KEY in .env and try again.")
        st.stop()


# ── Report display ────────────────────────────────────────────────────────────
if "report" in st.session_state:
    r = st.session_state.report
    st.divider()
    st.subheader("📊 Your Career Report")

    # Match score
    score = r.get("match_score", 0)
    emoji  = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
    verdict = "Strong match — apply with confidence" if score >= 70 \
        else "Decent match — worth applying" if score >= 50 \
        else "Significant gaps — consider upskilling first"

    score_col, bar_col = st.columns([1, 3])
    with score_col:
        st.metric("Match Score", f"{emoji} {score}%", verdict)
    with bar_col:
        st.write("")
        st.progress(score / 100)

    st.divider()

    # Skills
    skill_col1, skill_col2 = st.columns(2)
    with skill_col1:
        matched = r.get("matched_skills", [])
        st.success(
            "**✅ Skills you already have**\n\n" +
            ("\n".join(f"• {s}" for s in matched) if matched else "• None identified")
        )
    with skill_col2:
        missing = r.get("missing_skills", [])
        st.error(
            "**❌ Skills you're missing**\n\n" +
            ("\n".join(f"• {s}" for s in missing) if missing else "• No major gaps!")
        )

    # Strengths
    strengths = r.get("strengths", [])
    if strengths:
        st.info(
            "**💪 Strengths to highlight in your interview**\n\n" +
            "\n".join(f"• {s}" for s in strengths)
        )

    # Interview talking points
    points = r.get("interview_talking_points", [])
    if points:
        st.warning(
            "**💬 Interview talking points**\n\n" +
            "\n".join(f"{i+1}. {p}" for i, p in enumerate(points))
        )

    # Rewritten CV bullets
    bullets = r.get("rewritten_bullets", [])
    if bullets:
        st.subheader("✍️ Rewritten CV Bullets")
        st.caption("Tailored to this specific job — copy these directly into your CV")
        for bullet in bullets:
            st.code(bullet, language=None)

    # Download
    st.divider()
    dl_col, _ = st.columns([1, 2])
    with dl_col:
        st.download_button(
            label="⬇️ Download full report (JSON)",
            data=json.dumps(r, indent=2),
            file_name="jobsense_report.json",
            mime="application/json",
            use_container_width=True
        )

    # Footer note
    st.caption("💡 Tip: apply to different jobs? Click Clear above and run a fresh analysis.")


# ── Empty state ───────────────────────────────────────────────────────────────
if "report" not in st.session_state and not analyse:
    st.markdown("""
    <div style='text-align:center; padding: 3rem 0; color: #666;'>
        <div style='font-size: 3rem;'>🧠</div>
        <div style='font-size: 1.1rem; margin-top: 1rem;'>Upload your CV and paste a job description above</div>
        <div style='font-size: 0.9rem; margin-top: 0.5rem;'>You'll get a match score, gap analysis, and tailored interview prep in seconds</div>
    </div>
    """, unsafe_allow_html=True)