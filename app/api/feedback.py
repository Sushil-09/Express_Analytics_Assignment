import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter

from app.models.schemas import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)

FEEDBACK_FILE = Path("data/feedback.json")
_feedback_store: List[Dict[str, Any]] = []


def _save_feedback_to_disk(entry: Dict[str, Any]) -> None:
    try:
        FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        all_entries: List[Dict[str, Any]] = []
        if FEEDBACK_FILE.exists():
            try:
                with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                    all_entries = json.load(f)
            except Exception:
                all_entries = []
        all_entries.append(entry)
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(all_entries, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not persist feedback to disk: {e}")


@router.post("", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest):
    entry = {
        **request.model_dump(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _feedback_store.append(entry)
    _save_feedback_to_disk(entry)
    logger.info(f"Feedback received: rating={request.rating}, comment={request.comment}")
    return FeedbackResponse(
        message="Feedback submitted successfully",
        status="success"
    )


@router.get("", response_model=List[Dict[str, Any]])
def get_feedback():
    return _feedback_store

