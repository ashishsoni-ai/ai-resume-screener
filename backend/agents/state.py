"""
LangGraph State — the shared data structure passed between all agent nodes.

Think of this as the "brain" of the pipeline.
Every agent reads from and writes to this state.
TypedDict is required by LangGraph for state management.
"""
from typing import TypedDict, Any


class ResumeScreenerState(TypedDict):
    # Input
    raw_resume_text: str
    filename: str

    # Agent outputs — populated sequentially
    extracted_info: dict[str, Any]       # From InfoExtraction Agent
    skill_analysis: dict[str, Any]       # From SkillAnalysis Agent
    candidate_score: dict[str, Any]      # From Scoring Agent
    report_markdown: str                  # From Report Generator Agent

    # Error tracking
    errors: list[str]
    current_step: str
