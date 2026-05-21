"""
FastAPI Backend — Resume Screener API

Endpoints:
    POST /api/screen     - Upload resume, run pipeline, return results
    GET  /api/history    - Fetch all past screening sessions
    GET  /api/session/{id} - Fetch a specific session
    GET  /api/health     - Health check
"""
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from core.config import settings
from parsers.resume_parser import extract_resume_text
from agents.graph import run_screening_pipeline
from db.database import get_db, init_db
from db.models import ScreeningSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB tables on startup."""
    logger.info("🚀 Starting Resume Screener API...")
    os.makedirs(settings.upload_dir, exist_ok=True)
    init_db()
    logger.info("✅ DB initialized")
    yield
    logger.info("🛑 Shutting down")


app = FastAPI(
    title="AI Resume Screener",
    description="LangGraph-powered multi-agent resume screening system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/screen")
async def screen_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Main endpoint: accepts resume file, runs 4-agent pipeline, returns results.
    """
    # --- Validate file ---
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed_types = {".pdf", ".docx", ".doc"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Upload PDF or DOCX."
        )

    file_bytes = await file.read()
    if len(file_bytes) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size_mb}MB"
        )

    session_id = str(uuid.uuid4())
    logger.info(f"📄 New screening request | session={session_id} | file={file.filename}")

    # --- Extract text ---
    try:
        raw_text = extract_resume_text(file_bytes, file.filename)
        logger.info(f"✅ Text extracted: {len(raw_text)} chars")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # --- Run agent pipeline ---
    try:
        final_state = await run_screening_pipeline(raw_text, file.filename)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    # --- Persist to DB ---
    extracted = final_state.get("extracted_info", {})
    score_data = final_state.get("candidate_score", {})

    session = ScreeningSession(
        id=session_id,
        filename=file.filename,
        candidate_name=extracted.get("name"),
        final_score=score_data.get("final_score"),
        level=score_data.get("level"),
        hire_recommendation=score_data.get("hire_recommendation"),
        extracted_info_json=json.dumps(extracted),
        skill_analysis_json=json.dumps(final_state.get("skill_analysis", {})),
        candidate_score_json=json.dumps(score_data),
        report_markdown=final_state.get("report_markdown", ""),
    )
    db.add(session)
    db.commit()

    logger.info(f"✅ Session saved: {session_id} | Score: {score_data.get('final_score')}")

    return {
        "success": True,
        "session_id": session_id,
        "result": {
            "candidate_name": extracted.get("name"),
            "extracted_info": extracted,
            "skill_analysis": final_state.get("skill_analysis", {}),
            "candidate_score": score_data,
            "report_markdown": final_state.get("report_markdown", ""),
            "raw_resume_text": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
        },
    }


@app.get("/api/history")
async def get_history(db: Session = Depends(get_db)):
    """Returns all past screening sessions (most recent first)."""
    sessions = (
        db.query(ScreeningSession)
        .order_by(ScreeningSession.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "sessions": [
            {
                "session_id": s.id,
                "filename": s.filename,
                "candidate_name": s.candidate_name,
                "final_score": s.final_score,
                "level": s.level,
                "hire_recommendation": s.hire_recommendation,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sessions
        ]
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Returns full details of a specific screening session."""
    session = db.query(ScreeningSession).filter(ScreeningSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()
