"""
Prompt templates for each agent in the pipeline.
Keep prompts strict and structured — LLMs follow format better with examples.
"""

EXTRACTION_PROMPT = """You are an expert resume parser. Extract structured information from the resume text below.

Return ONLY valid JSON matching this exact schema — no markdown, no explanation:

{{
  "name": "candidate full name or null",
  "email": "email or null",
  "phone": "phone number or null",
  "education": [
    {{
      "degree": "degree name",
      "institution": "college/university",
      "year": "graduation year or expected year"
    }}
  ],
  "experience": [
    {{
      "role": "job title",
      "company": "company name",
      "duration": "e.g. Jan 2023 - Jun 2024",
      "description": "brief summary of responsibilities"
    }}
  ],
  "projects": [
    {{
      "name": "project name",
      "description": "what it does",
      "technologies": ["tech1", "tech2"],
      "highlights": "most impressive aspect"
    }}
  ],
  "skills": {{
    "languages": ["Python", "JavaScript"],
    "frameworks": ["FastAPI", "React"],
    "ml_tools": ["TensorFlow", "LangChain"],
    "databases": ["PostgreSQL", "MongoDB"],
    "cloud_devops": ["AWS", "Docker"],
    "other": ["Git", "REST APIs"]
  }},
  "certifications": ["cert1", "cert2"],
  "total_experience_years": 0.0
}}

RESUME TEXT:
{resume_text}
"""

SKILL_ANALYSIS_PROMPT = """You are a senior technical interviewer evaluating a candidate's skill depth.

Given the extracted resume data below, score each skill category on a scale of 0-10.
Base scores on: years of experience, project complexity, technologies mentioned, and real-world application.

Return ONLY valid JSON — no markdown, no explanation:

{{
  "python": {{
    "score": 7,
    "evidence": "Used FastAPI and LangChain across 3 production-grade projects"
  }},
  "machine_learning": {{
    "score": 6,
    "evidence": "Built CNN, used YOLOv8, but no mention of deployment or MLOps"
  }},
  "llm_genai": {{
    "score": 8,
    "evidence": "RAG pipeline, LangGraph agentic system, Groq API integration"
  }},
  "backend_engineering": {{
    "score": 7,
    "evidence": "FastAPI with WebSocket, REST APIs, Render deployment"
  }},
  "project_complexity": {{
    "score": 7,
    "evidence": "Multi-agent system for medical emergency detection shows systems thinking"
  }},
  "overall_reasoning": "Candidate is a strong intermediate-level AI/ML engineer with clear specialization in LLM applications."
}}

EXTRACTED RESUME DATA:
{extracted_data}
"""

SCORING_PROMPT = """You are a technical recruiter making a final hiring recommendation.

Given the skill scores and resume data, produce a final candidate assessment.

Return ONLY valid JSON — no markdown, no explanation:

{{
  "final_score": 72,
  "level": "Intermediate",
  "hire_recommendation": "Strong Yes / Yes / Maybe / No",
  "strengths": [
    "Strong LLM and agentic workflow experience",
    "Ships real end-to-end projects"
  ],
  "gaps": [
    "Limited system design knowledge",
    "No production deployment experience"
  ],
  "suggested_interview_questions": [
    "Walk me through how you designed your LangGraph pipeline.",
    "How would you scale this system to handle 1000 resumes/day?"
  ],
  "resume_improvement_tips": [
    "Quantify project impact with metrics",
    "Add a GitHub link to each project"
  ],
  "summary": "2-3 sentence recruiter-friendly summary of the candidate"
}}

SKILL SCORES:
{skill_scores}

EXTRACTED DATA:
{extracted_data}

SCORING RUBRIC:
- 0-40: Beginner
- 41-65: Intermediate
- 66-85: Advanced
- 86-100: Expert

Each of the 5 skill dimensions contributes max 20 points to the final score.
"""

REPORT_PROMPT = """You are writing a professional recruiter report for a candidate.

Based on all analysis, write a clean, professional markdown report.
Be honest, specific, and helpful. Use data from the scoring.

Return the report in clean markdown format with these sections:
# Candidate Report: {{name}}

## 📋 Summary
(2-3 sentences)

## 🎯 Tech Proficiency Level: {{level}} ({{score}}/100)

## ✅ Strengths
- ...

## ⚠️ Gaps
- ...

## 💡 Interview Questions
1. ...

## 📈 Resume Tips
- ...

FULL ANALYSIS DATA:
{full_analysis}
"""
