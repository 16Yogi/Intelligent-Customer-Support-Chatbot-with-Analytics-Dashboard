from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..agent import get_agent


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=schemas.ChatMessageOut)
def chat(message: schemas.ChatMessageIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == message.user_id).first()
    if not user:
        user = models.User(
            id=message.user_id,
            name="Demo User",
            email=f"demo{message.user_id}@example.com",
        )
        db.add(user)
        db.flush()

    if message.conversation_id:
        conversation = (
            db.query(models.Conversation)
            .filter(
                models.Conversation.id == message.conversation_id,
                models.Conversation.user_id == user.id,
            )
            .first()
        )
    else:
        conversation = None

    if not conversation:
        conversation = models.Conversation(user_id=user.id, status="open", channel="web")
        db.add(conversation)
        db.flush()

    user_msg = models.Message(
        conversation_id=conversation.id,
        sender="user",
        text=message.text,
    )
    db.add(user_msg)

    start = perf_counter()
    agent = get_agent()
    reply_text, intent = agent.reply(message.text)
    latency_ms = int((perf_counter() - start) * 1000)

    bot_msg = models.Message(
        conversation_id=conversation.id,
        sender="bot",
        text=reply_text,
        intent=intent,
        entities={},
        latency_ms=latency_ms,
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    return schemas.ChatMessageOut(
        conversation_id=conversation.id,
        reply=bot_msg.text,
        intent=bot_msg.intent or "unknown",
        created_at=bot_msg.created_at,
    )

