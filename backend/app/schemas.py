from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    user_id: int
    text: str
    conversation_id: Optional[int] = None


class ChatMessageOut(BaseModel):
    conversation_id: int
    reply: str
    intent: str
    created_at: datetime


class AnalyticsSummary(BaseModel):
    total_conversations: int
    total_messages: int
    avg_response_time_ms: Optional[float]
    top_intents: List[Dict[str, Any]]


class FeedbackIn(BaseModel):
    conversation_id: int
    rating: int
    comment: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    conversation_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

