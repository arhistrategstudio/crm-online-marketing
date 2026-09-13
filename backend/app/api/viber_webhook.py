import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.models import Channel, Contact, Conversation, Message
from app.services.viber import verify_signature


router = APIRouter(prefix="/webhooks/viber", tags=["Viber"])


@router.post("", status_code=status.HTTP_200_OK)
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Ingests Viber Bot API webhook events. Viber requires a 200 with an (optionally empty)
    JSON body for every event type — including its own "webhook" verification ping sent right
    after `set_webhook` — so unrecognized events are acknowledged without side effects."""
    raw_body = await request.body()
    signature = request.headers.get("X-Viber-Content-Signature")
    if settings.viber_auth_token and not verify_signature(raw_body, signature, settings.viber_auth_token):
        raise HTTPException(status_code=403, detail="Nevažeći potpis webhook-a.")

    try:
        payload = json.loads(raw_body or b"{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Neispravan JSON.")

    if payload.get("event") == "message":
        _handle_incoming_message(db, payload)

    return {"status": 0}


def _handle_incoming_message(db: Session, payload: dict) -> None:
    sender = payload.get("sender") or {}
    viber_id = sender.get("id")
    text = (payload.get("message") or {}).get("text")
    if not viber_id or not text:
        return

    contact = db.scalar(select(Contact).where(Contact.external_id == viber_id))
    if not contact:
        contact = Contact(name=sender.get("name") or "Viber korisnik", source=Channel.viber, external_id=viber_id)
        db.add(contact)
        db.flush()

    conversation = db.scalar(
        select(Conversation).where(Conversation.contact_id == contact.id, Conversation.channel == Channel.viber)
    )
    if not conversation:
        conversation = Conversation(contact_id=contact.id, channel=Channel.viber, external_id=viber_id)
        db.add(conversation)
        db.flush()
    else:
        conversation.unread_count += 1

    db.add(Message(conversation_id=conversation.id, sender="contact", content=text, status="received"))
    db.commit()
