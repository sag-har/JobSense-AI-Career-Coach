import os
import json
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from schema import CareerReport


def get_groq_key():
    """Read API key from .env locally or st.secrets on Streamlit Cloud."""
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.getenv("GROQ_API_KEY")


def generate_report(cv_store: FAISS, jd_store: FAISS) -> dict:
    """
    Cross-query both FAISS stores and generate a structured career report.
    Uses Groq (free) with Llama 3.3 70B.
    """

    # Step 1 — retrieve relevant chunks from BOTH vector stores
    cv_chunks = cv_store.similarity_search(
        "skills experience projects education background achievements", k=6
    )
    jd_chunks = jd_store.similarity_search(
        "required skills qualifications responsibilities experience", k=6
    )

    cv_context = "\n\n".join([c.page_content for c in cv_chunks])
    jd_context = "\n\n".join([c.page_content for c in jd_chunks])

    # Step 2 — build prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior technical recruiter and career coach with 10 years of experience.
Carefully analyse the candidate CV against the job description below.

CV CONTENT:
{cv_context}

JOB DESCRIPTION:
{jd_context}

Return ONLY a valid JSON object with exactly these keys — no markdown, no explanation, just JSON:

{{
  "match_score": <integer 0-100>,
  "matched_skills": [<list of specific technologies/skills the candidate has that the JD wants>],
  "missing_skills": [<list of specific skills/technologies the JD requires but candidate lacks>],
  "strengths": [<list of exactly 3 strings — specific strengths to highlight in the interview>],
  "rewritten_bullets": [<list of exactly 3 strings — improved CV bullet points tailored to this JD, starting with strong action verbs>],
  "interview_talking_points": [<list of exactly 5 strings — concrete things to say in the interview>]
}}

Rules:
- Be specific — name actual technologies, not vague categories like "programming"
- rewritten_bullets must start with a strong action verb (Built, Designed, Led, Reduced, Increased)
- match_score should reflect realistic fit — 50 means worth applying, 70+ means strong match
- Do NOT wrap in markdown code fences"""),
        ("human", "Generate the career gap analysis report now.")
    ])

    # Step 3 — call Groq (free, fast)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=2048,
        api_key=get_groq_key()
    )

    chain = prompt | llm
    response = chain.invoke({
        "cv_context": cv_context,
        "jd_context": jd_context
    })

    # Step 4 — parse JSON safely
    raw = response.content.strip()

    # Strip markdown fences if Llama wraps output anyway
    raw = re.sub(r'```(?:json)?|```', '', raw).strip()

    # Extract JSON object if there's extra text around it
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group()

    try:
        data = json.loads(raw)
        report = CareerReport(**data)
        return report.model_dump()
    except Exception as e:
        # Return a safe fallback so the UI never crashes
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "strengths": [f"Error generating report: {str(e)}"],
            "rewritten_bullets": [f"Raw response: {raw[:300]}"],
            "interview_talking_points": ["Please try again — Groq occasionally has hiccups"]
        }