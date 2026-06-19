# 🧠 JobSense — AI Career Coach

> Upload your CV. Paste a job description. Get your match score, skill gap analysis, tailored interview talking points, and rewritten CV bullets — in under 10 seconds.

> 🎬 **Live demo:**

![JobSense Demo](demo.gif)

> 

![JobSense Screenshot](screenshot.png)

👉 **[Try JobSense Live →](https://jobsense-ai-career-coach-g9ucp9ucell8uzph7zrb2e.streamlit.app/)**





[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=for-the-badge)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=for-the-badge)](https://groq.com)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-0057B7?style=for-the-badge)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Click%20Here-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://jobsense-ai-career-coach-g9ucp9ucell8uzph7zrb2e.streamlit.app/)

---

## ✨ What it does

Most people apply to jobs blindly — sending the same CV everywhere and hoping for the best. **JobSense** fixes that.

Upload your CV (PDF) and paste any job description. The app uses **Retrieval-Augmented Generation (RAG)** to cross-reference both documents via two independent FAISS vector stores, then produces a structured career report with:

| Output | What you get |
|---|---|
| 📊 **Match Score** | 0–100% score showing how well your CV fits the role |
| ✅ **Matched Skills** | Skills you already have that the JD is asking for |
| ❌ **Skill Gaps** | Missing skills you need to develop or address |
| 💪 **Strengths** | Your strongest selling points for this specific role |
| 💬 **Interview Talking Points** | 5 ready-to-use points tailored to this JD |
| ✍️ **Rewritten CV Bullets** | 3 bullets rewritten to match the job's language and priorities |

---

## 🏗️ Architecture

```
CV (PDF)         ──► PyMuPDF ──► Text Chunks ──► HuggingFace Embeddings ──► FAISS Store A ──┐
                                                                                              ├──► Similarity Search
Job Description  ──► Splitter ──► Text Chunks ──► HuggingFace Embeddings ──► FAISS Store B ──┘
                                                                                              │
                                                                          Retrieved Context ──┤
                                                                                              ▼
                                                              System Prompt + RAG Context ──► Llama 3.3 70B (Groq)
                                                                                              │
                                                                                              ▼
                                                                           Pydantic Parser ──► Structured JSON
                                                                                              │
                                                                                              ▼
                                                                               Streamlit UI ──► You
```

**Why two FAISS stores?** Most RAG tutorials query a single document. JobSense cross-references two separate vector stores simultaneously — querying your CV against the job description's requirements. This is the same pattern used in enterprise systems that match user profiles against policy or requirements databases.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM | Llama 3.3 70B via Groq | Ultra-fast inference for structured analysis |
| Vector DB | FAISS (local, CPU) | Zero cost, zero latency, no external service needed |
| Embeddings | `sentence-transformers` (HuggingFace) | Local embeddings — no API key needed |
| Document parsing | PyMuPDF | Reliable text extraction from real-world PDFs |
| Output schema | Pydantic v2 | Guarantees structured JSON every time |
| Orchestration | LangChain 0.3 LCEL | Clean pipeline: prompt → llm → parser |
| UI | Streamlit 1.45 | Deployed and shareable in minutes |

---

## 📁 Project Structure

```
JobSense-AI-Career-Coach/
├── app.py              # Streamlit UI — upload, report rendering, buttons
├── ingest.py           # PDF/text → chunks → embeddings → FAISS vector store
├── generate.py         # Retrieval chain + Llama 3.3 70B + structured output
├── schema.py           # CareerReport Pydantic model (the JSON contract)
├── requirements.txt    # All dependencies pinned
├── .env                # Your GROQ_API_KEY (never commit this)
├── .gitignore          # Excludes .env and __pycache__
└── README.md
```

---

## ⚡ Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/sag-har/JobSense-AI-Career-Coach.git
cd JobSense-AI-Career-Coach
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Create a `.env` file in the project root:
```
GROQ_API_KEY=gsk_your_key_here
```
Get a **free** key at [console.groq.com](https://console.groq.com) — no credit card required.

**5. Run**
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🚀 Deploy on Streamlit Cloud (Free)

### Step 1 — Make sure `.env` is in `.gitignore`
```
.env
__pycache__/
*.pyc
```

### Step 2 — Push to GitHub
Your repo should be public at `github.com/muneeracodes/JobSense-AI-Career-Coach`.

### Step 3 — Go to Streamlit Cloud
Visit [share.streamlit.io](https://share.streamlit.io) → sign in with GitHub → click **"Create app"**.

### Step 4 — Fill in the form
| Field | Value |
|---|---|
| Repository | `sag-har/JobSense-AI-Career-Coach` |
| Branch | `main` |
| Main file path | `app.py` |

### Step 5 — Add your secret key
Click **"Advanced settings"** → **"Secrets"** → paste:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```

> ⚠️ Never put your API key in any committed file. Streamlit Secrets is the correct way.

### Step 6 — Deploy
Click **"Deploy"**. In ~2 minutes you get a live public URL:
```
https://jobsense-ai-career-coach-g9ucp9ucell8uzph7zrb2e.streamlit.app/
```

---

## 📊 Example Report Output

```json
{
  "match_score": 74,
  "matched_skills": ["Python", "Django", "REST APIs", "PostgreSQL", "Git"],
  "missing_skills": ["Kubernetes", "AWS Lambda", "Redis"],
  "strengths": [
    "3 years of production Django experience directly matches the JD requirement",
    "Open source contributions demonstrate code quality and collaboration",
    "PostgreSQL expertise fully covers the database requirement"
  ],
  "rewritten_bullets": [
    "Architected and deployed a Django REST API serving 50k+ daily requests with 99.9% uptime",
    "Reduced query response time by 40% through PostgreSQL indexing and query optimisation",
    "Led migration of a monolithic Flask app to microservices, cutting deploy time by 60%"
  ],
  "interview_talking_points": [
    "Lead with your Django production experience — it directly matches their core requirement",
    "Frame your REST API work in terms of scale and uptime, not just features built",
    "For the Kubernetes gap: mention you're actively learning it and show your progress",
    "Use your open source contributions as proof of code review and collaboration",
    "Ask about their infrastructure pain points — shows strategic thinking"
  ]
}
```

---

## ⚠️ Known Limitations

- **Scanned PDFs not supported** — requires text-based PDFs; OCR support is planned
- **English only** — prompt engineering is optimised for English JDs and CVs
- **Session-based** — report resets on page refresh (by design for privacy)

---

## 🗺️ Roadmap

- [ ] OCR support for scanned CVs (Tesseract / AWS Textract)
- [ ] Export report as styled PDF
- [ ] Compare multiple job descriptions side by side
- [ ] LinkedIn JD auto-import via URL
- [ ] RAGAS evaluation for retrieval quality scoring

---

## 🧑‍💻 Built by

**Saghar** — [@sag-har](https://github.com/sag-har)
🚀 **Live App:** [jobsense-ai-career-coach-g9ucp9ucell8uzph7zrb2e.streamlit.app](https://jobsense-ai-career-coach-g9ucp9ucell8uzph7zrb2e.streamlit.app/)
Built to solve a real problem while job hunting — and as a portfolio project demonstrating LangChain RAG with dual vector stores.

---

## 📄 License

MIT — use it, fork it, improve it. Attribution appreciated but not required.
