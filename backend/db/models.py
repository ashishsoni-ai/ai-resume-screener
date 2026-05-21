"""
ORM Models — defines the database schema.

We store results as JSON strings for simplicity.
Production alternative: separate tables for skills, projects, etc.
"""
import json
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from db.database import Base


class ScreeningSession(Base):
    __tablename__ = "screening_sessions"

    id = Column(String, primary_key=True)  # UUID
    filename = Column(String, nullable=False)
    candidate_name = Column(String, nullable=True)
    final_score = Column(Integer, nullable=True)
    level = Column(String, nullable=True)           # Beginner / Intermediate / etc.
    hire_recommendation = Column(String, nullable=True)
    extracted_info_json = Column(Text, nullable=True)   # JSON blob
    skill_analysis_json = Column(Text, nullable=True)   # JSON blob
    candidate_score_json = Column(Text, nullable=True)  # JSON blob
    report_markdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "session_id": self.id,
            "filename": self.filename,
            "candidate_name": self.candidate_name,
            "final_score": self.final_score,
            "level": self.level,
            "hire_recommendation": self.hire_recommendation,
            "extracted_info": json.loads(self.extracted_info_json or "{}"),
            "skill_analysis": json.loads(self.skill_analysis_json or "{}"),
            "candidate_score": json.loads(self.candidate_score_json or "{}"),
            "report_markdown": self.report_markdown,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
