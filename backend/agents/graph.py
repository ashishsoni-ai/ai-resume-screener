import logging
from langgraph.graph import StateGraph, END

from agents.state import ResumeScreenerState
from agents.nodes import (
    info_extraction_agent,
    skill_analysis_agent,
    scoring_agent,
    report_generator_agent,
)

logger = logging.getLogger(__name__)


def build_screening_graph() -> StateGraph:
    graph = StateGraph(ResumeScreenerState)

    # Node names must NOT match state key names — added _node suffix
    graph.add_node("extract_info_node", info_extraction_agent)
    graph.add_node("analyze_skills_node", skill_analysis_agent)
    graph.add_node("score_candidate_node", scoring_agent)
    graph.add_node("generate_report_node", report_generator_agent)

    graph.set_entry_point("extract_info_node")
    graph.add_edge("extract_info_node", "analyze_skills_node")
    graph.add_edge("analyze_skills_node", "score_candidate_node")
    graph.add_edge("score_candidate_node", "generate_report_node")
    graph.add_edge("generate_report_node", END)

    return graph.compile()


screening_graph = build_screening_graph()


async def run_screening_pipeline(raw_text: str, filename: str) -> dict:
    logger.info(f"🚀 Starting screening pipeline for: {filename}")

    initial_state: ResumeScreenerState = {
        "raw_resume_text": raw_text,
        "filename": filename,
        "extracted_info": {},
        "skill_analysis": {},
        "candidate_score": {},
        "report_markdown": "",
        "errors": [],
        "current_step": "started",
    }

    final_state = await screening_graph.ainvoke(initial_state)
    logger.info(f"✅ Pipeline complete. Step: {final_state.get('current_step')}")
    return final_state