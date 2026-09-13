from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.models import Channel, Contact, Conversation, Message
from app.schemas.conversation import ConversationRead, MessageCreate, MessageRead
from app.services.viber import send_message as send_viber_message


router = APIRouter(prefix="/conversations", tags=["Inbox"])


def conversation_or_404(conversation_id: int, db: Session) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Razgovor nije pronađen.")
    return conversation


def _conversation_summary(db: Session, conversation: Conversation, contact: Contact) -> ConversationRead:
    last_message = db.scalar(
        select(Message.content)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.id.desc())
        .limit(1)
    )
    return ConversationRead(
        id=conversation.id,
        contact_id=contact.id,
        contact_name=contact.name,
        channel=conversation.channel,
        unread_count=conversation.unread_count,
        last_message=last_message,
        created_at=conversation.created_at,
    )


@router.get("", response_model=list[ConversationRead])
def list_conversations(db: Session = Depends(get_db)) -> list[ConversationRead]:
    rows = db.execute(
        select(Conversation, Contact)
        .join(Contact, Conversation.contact_id == Contact.id)
        .order_by(Conversation.created_at.desc())
    ).all()
    return [_conversation_summary(db, conversation, contact) for conversation, contact in rows]


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)) -> ConversationRead:
    conversation = conversation_or_404(conversation_id, db)
    return _conversation_summary(db, conversation, conversation.contact)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def list_messages(conversation_id: int, db: Session = Depends(get_db)) -> list[Message]:
    conversation = conversation_or_404(conversation_id, db)
    if conversation.unread_count:
        conversation.unread_count = 0
        db.commit()
    return list(db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id)))


@router.post("/{conversation_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(
    conversation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Message:
    conversation = conversation_or_404(conversation_id, db)
    message = Message(conversation_id=conversation_id, sender="agent", content=data.content)
    db.add(message)
    db.commit()
    db.refresh(message)

    if conversation.channel == Channel.viber and settings.viber_auth_token and conversation.external_id:
        try:
            send_viber_message(conversation.external_id, data.content, settings.viber_auth_token)
            message.status = "sent"
        except Exception:  # noqa: BLE001 - keep the message saved even if the Viber API call fails
            message.status = "failed"
        db.commit()
        db.refresh(message)

    return message
