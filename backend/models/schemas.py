"""
Pydantic schemas for API I/O.
These define the contract between frontend, backend, and agents.
"""
from typing import Any
from pydantic import BaseModel


# --- Resume parser output ---

class EducationItem(BaseModel):
    degree: str
    institution: str
    year: str


class ExperienceItem(BaseModel):
    role: str
    company: str
    duration: str
    description: str


class ProjectItem(BaseModel):
    name: str
    description: str
    technologies: list[str]
    highlights: str


class SkillSet(BaseModel):
    languages: list[str] = []
    frameworks: list[str] = []
    ml_tools: list[str] = []
    databases: list[str] = []
    cloud_devops: list[str] = []
    other: list[str] = []


class ExtractedInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    education: list[EducationItem] = []
    experience: list[ExperienceItem] = []
    projects: list[ProjectItem] = []
    skills: SkillSet = SkillSet()
    certifications: list[str] = []
    total_experience_years: float = 0.0


# --- Skill analysis output ---

class SkillDimension(BaseModel):
    score: int
    evidence: str


class SkillAnalysis(BaseModel):
    python: SkillDimension
    machine_learning: SkillDimension
    llm_genai: SkillDimension
    backend_engineering: SkillDimension
    project_complexity: SkillDimension
    overall_reasoning: str


# --- Scoring output ---

class CandidateScore(BaseModel):
    final_score: int
    level: str  # Beginner / Intermediate / Advanced / Expert
    hire_recommendation: str
    strengths: list[str]
    gaps: list[str]
    suggested_interview_questions: list[str]
    resume_improvement_tips: list[str]
    summary: str


# --- Full pipeline result ---

class ScreeningResult(BaseModel):
    candidate_name: str | None
    extracted_info: ExtractedInfo
    skill_analysis: SkillAnalysis
    candidate_score: CandidateScore
    report_markdown: str
    raw_resume_text: str


# --- API response ---

class ScreeningResponse(BaseModel):
    success: bool
    session_id: str
    result: ScreeningResult | None = None
    error: str | None = None


class HistoryItem(BaseModel):
    session_id: str
    candidate_name: str | None
    final_score: int
    level: str
    created_at: str
