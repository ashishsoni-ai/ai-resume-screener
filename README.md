# 🎯 AI Resume Screener

A **multi-agent LangGraph pipeline** that screens resumes using LLM reasoning, extracts structured candidate information, and produces tech proficiency scores with detailed recruiter reports.

Built as a submission for a technical assessment — designed to be **functional, clean, and production-style**.

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────────┐
                    │         LangGraph Agent Pipeline         │
                    │                                         │
  PDF / DOCX  ──►  │  [Parser] → [InfoExtraction] →          │
                    │  [SkillAnalysis] → [Scoring] →          │
                    │  [ReportGenerator]                       │
                    │                                         │
                    └────────────────┬────────────────────────┘
                                     │
                              FastAPI Backend
                                     │
                             Streamlit Frontend
```

### Agent Pipeline (4 agents via LangGraph)

| Agent | Role | Output |
|-------|------|--------|
| **Info Extraction** | Parses skills, projects, experience, education from raw text | Structured JSON |
| **Skill Analysis** | Scores 5 technical dimensions (0-10 each) with evidence | Skill scores + reasoning |
| **Scoring** | Produces final 0-100 score, level, hire recommendation | Candidate report data |
| **Report Generator** | Generates markdown recruiter report | Human-readable report |

### Scoring Framework

| Dimension | Weight |
|-----------|--------|
| Python Proficiency | /10 |
| Machine Learning | /10 |
| LLM / GenAI | /10 |
| Backend Engineering | /10 |
| Project Complexity | /10 |

Final level thresholds: **Beginner** (0-40) · **Intermediate** (41-65) · **Advanced** (66-85) · **Expert** (86-100)

---

## 🛠️ Tech Stack

- **Backend:** FastAPI + SQLAlchemy (SQLite)
- **Agent Orchestration:** LangGraph
- **LLM:** Groq (LLaMA 3.3 70B) — free tier, fast
- **Resume Parsing:** pdfplumber + python-docx
- **Frontend:** Streamlit
- **Deployment:** Render (backend) + Streamlit Cloud (frontend)

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/ashishsoni-ai/ai-resume-screener
cd ai-resume-screener
```

### 2. Set up backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in `/backend`:
```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Get a free Groq API key at: https://console.groq.com

### 3. Run backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 4. Set up and run frontend

```bash
cd frontend
pip install -r requirements.txt

# Create .env
echo "BACKEND_URL=http://localhost:8000" > .env

streamlit run app.py
```

Open: http://localhost:8501

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/screen` | Upload resume, run pipeline |
| `GET` | `/api/history` | Fetch all past sessions |
| `GET` | `/api/session/{id}` | Fetch specific session |
| `GET` | `/api/health` | Health check |

Full interactive docs: `http://localhost:8000/docs`

---

## 🗂️ Project Structure

```
resume-screener/
├── backend/
│   ├── main.py                 # FastAPI app + routes
│   ├── agents/
│   │   ├── state.py            # LangGraph TypedDict state
│   │   ├── nodes.py            # 4 agent node functions
│   │   └── graph.py            # Pipeline wiring
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   └── prompts.py          # All prompt templates
│   ├── parsers/
│   │   └── resume_parser.py    # PDF + DOCX extraction
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── db/
│   │   ├── database.py         # SQLAlchemy setup
│   │   └── models.py           # ORM models
│   └── requirements.txt
├── frontend/
│   └── app.py                  # Streamlit UI
├── .env.example
└── README.md
```

---

## 🚢 Deployment

### Backend → Render

1. Push to GitHub
2. Create new **Web Service** on Render
3. Set **Root Directory** to `backend`
4. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `GROQ_API_KEY`

### Frontend → Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Connect your GitHub repo
3. Set **Main file path**: `frontend/app.py`
4. Add secret: `BACKEND_URL=https://your-render-url.onrender.com`

---

## 💡 Design Decisions

- **Groq over OpenAI**: Free tier, LLaMA 3.3 70B, ~10x faster than GPT-4o for structured extraction
- **Streamlit over React**: Faster to ship, clean enough for demo, focus stays on AI pipeline
- **LangGraph over plain LangChain**: State isolation per step, visualizable, extensible with conditional edges
- **pdfplumber over PyPDF2**: Handles multi-column layouts and tables common in modern resumes
- **SQLite**: Zero config, good enough for demo, swap to Postgres on Render for production

---

## 👤 Author

**Ashish Soni**  
B.Tech AI & ML · GGSIPU · CGPA 9.19  
GitHub: [github.com/ashishsoni-ai](https://github.com/ashishsoni-ai)
