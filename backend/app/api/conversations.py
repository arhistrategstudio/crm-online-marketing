from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Conversation, Message
from app.schemas.conversation import ConversationRead, MessageCreate, MessageRead


router = APIRouter(prefix="/conversations", tags=["Inbox"])


def conversation_or_404(conversation_id: int, db: Session) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Razgovor nije pronađen.")
    return conversation


@router.get("", response_model=list[ConversationRead])
def list_conversations(db: Session = Depends(get_db)) -> list[Conversation]:
    return list(db.scalars(select(Conversation).order_by(Conversation.created_at.desc())))


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)) -> Conversation:
    return conversation_or_404(conversation_id, db)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def list_messages(conversation_id: int, db: Session = Depends(get_db)) -> list[Message]:
    conversation_or_404(conversation_id, db)
    return list(db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id)))


@router.post("/{conversation_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(conversation_id: int, data: MessageCreate, db: Session = Depends(get_db)) -> Message:
    conversation_or_404(conversation_id, db)
    message = Message(conversation_id=conversation_id, sender="agent", content=data.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
