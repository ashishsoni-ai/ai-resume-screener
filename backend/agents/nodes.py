"""
Agent Nodes — each function is one step in the LangGraph pipeline.

Design principle: each node is a pure function that:
1. Reads what it needs from state
2. Calls LLM with a structured prompt
3. Parses response to JSON
4. Returns partial state update

Why JSON parsing with fallback?
LLMs occasionally drift from format. Robust parsing prevents pipeline crashes.
"""
import json
import logging
import re
from typing import Any

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

from core.config import settings
from core.prompts import (
    EXTRACTION_PROMPT,
    SKILL_ANALYSIS_PROMPT,
    SCORING_PROMPT,
    REPORT_PROMPT,
)
from agents.state import ResumeScreenerState

logger = logging.getLogger(__name__)

# Single LLM instance shared across all agents (efficient, no re-init overhead)
llm = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.groq_model,
    temperature=0.1,  # Low temp = more deterministic, better for structured output
)


def _call_llm_json(prompt: str, step_name: str) -> dict[str, Any]:
    """
    Calls LLM and safely parses JSON response.
    Extracts JSON even if LLM wraps it in markdown code blocks.
    """
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_text = response.content.strip()

        # Strip markdown code fences if present (LLMs sometimes add them)
        raw_text = re.sub(r"```json\s*", "", raw_text)
        raw_text = re.sub(r"```\s*", "", raw_text)
        raw_text = raw_text.strip()

        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        logger.error(f"[{step_name}] JSON parse failed: {e}\nRaw: {raw_text[:500]}")
        raise ValueError(f"LLM returned invalid JSON at step: {step_name}")
    except Exception as e:
        logger.error(f"[{step_name}] LLM call failed: {e}")
        raise


# ─────────────────────────────────────────────
# AGENT 1: Info Extraction
# ─────────────────────────────────────────────

def info_extraction_agent(state: ResumeScreenerState) -> dict:
    """
    Extracts structured information from raw resume text.
    Output: name, email, skills, projects, experience, education.
    """
    logger.info("🤖 Agent 1: Info Extraction running...")

    prompt = EXTRACTION_PROMPT.format(resume_text=state["raw_resume_text"])
    extracted = _call_llm_json(prompt, "InfoExtraction")

    return {
        "extracted_info": extracted,
        "current_step": "info_extraction_done",
    }


# ─────────────────────────────────────────────
# AGENT 2: Skill Analysis
# ─────────────────────────────────────────────

def skill_analysis_agent(state: ResumeScreenerState) -> dict:
    """
    Evaluates depth of skills across 5 technical dimensions.
    Each dimension scored 0-10 with evidence from the resume.
    """
    logger.info("🤖 Agent 2: Skill Analysis running...")

    extracted_str = json.dumps(state["extracted_info"], indent=2)
    prompt = SKILL_ANALYSIS_PROMPT.format(extracted_data=extracted_str)
    skill_analysis = _call_llm_json(prompt, "SkillAnalysis")

    return {
        "skill_analysis": skill_analysis,
        "current_step": "skill_analysis_done",
    }


# ─────────────────────────────────────────────
# AGENT 3: Scoring
# ─────────────────────────────────────────────

def scoring_agent(state: ResumeScreenerState) -> dict:
    """
    Produces final candidate score (0-100), level, hire recommendation,
    strengths, gaps, and interview questions.
    """
    logger.info("🤖 Agent 3: Scoring running...")

    skill_scores_str = json.dumps(state["skill_analysis"], indent=2)
    extracted_str = json.dumps(state["extracted_info"], indent=2)

    prompt = SCORING_PROMPT.format(
        skill_scores=skill_scores_str,
        extracted_data=extracted_str,
    )
    candidate_score = _call_llm_json(prompt, "Scoring")

    return {
        "candidate_score": candidate_score,
        "current_step": "scoring_done",
    }


# ─────────────────────────────────────────────
# AGENT 4: Report Generator
# ─────────────────────────────────────────────

def report_generator_agent(state: ResumeScreenerState) -> dict:
    """
    Generates a human-readable recruiter report in Markdown format.
    This is the final output users will see.
    """
    logger.info("🤖 Agent 4: Report Generation running...")

    full_analysis = {
        "extracted_info": state["extracted_info"],
        "skill_analysis": state["skill_analysis"],
        "candidate_score": state["candidate_score"],
    }

    prompt = REPORT_PROMPT.format(full_analysis=json.dumps(full_analysis, indent=2))

    # Report is markdown, not JSON — direct LLM call
    response = llm.invoke([HumanMessage(content=prompt)])
    report_markdown = response.content.strip()

    return {
        "report_markdown": report_markdown,
        "current_step": "complete",
    }
