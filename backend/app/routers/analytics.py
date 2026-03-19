from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=schemas.AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    total_conversations = db.query(func.count(models.Conversation.id)).scalar() or 0
    total_messages = db.query(func.count(models.Message.id)).scalar() or 0

    avg_response_time = (
        db.query(func.avg(models.Message.latency_ms))
        .filter(models.Message.sender == "bot", models.Message.latency_ms.isnot(None))
        .scalar()
    )

    intent_counts: List[Dict[str, Any]] = (
        db.query(models.Message.intent, func.count(models.Message.id).label("count"))
        .filter(models.Message.sender == "bot", models.Message.intent.isnot(None))
        .group_by(models.Message.intent)
        .order_by(func.count(models.Message.id).desc())
        .limit(5)
        .all()
    )

    top_intents = [
        {"intent": row.intent or "unknown", "count": row.count} for row in intent_counts
    ]

    return schemas.AnalyticsSummary(
        total_conversations=total_conversations,
        total_messages=total_messages,
        avg_response_time_ms=float(avg_response_time) if avg_response_time else None,
        top_intents=top_intents,
    )

