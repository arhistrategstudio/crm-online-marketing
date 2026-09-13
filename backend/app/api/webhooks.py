import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.models import Channel, Contact, Lead, MetaLeadEvent
from app.services.meta import detect_platform, extract_contact_fields, fetch_lead_data, verify_signature


router = APIRouter(prefix="/webhooks/meta", tags=["Meta Lead Ads"])
logger = logging.getLogger(__name__)


@router.get("")
def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
    settings: Settings = Depends(get_settings),
) -> Response:
    """Meta's one-time handshake when the webhook subscription is registered in Meta App settings."""
    token_ok = settings.meta_verify_token and hub_verify_token == settings.meta_verify_token
    if hub_mode != "subscribe" or not token_ok or not hub_challenge:
        raise HTTPException(status_code=403, detail="Verifikacija webhook-a nije uspela.")
    return Response(content=hub_challenge, media_type="text/plain")


def _find_or_create_contact(db: Session, leadgen_id: str, fields: dict[str, str | None], channel: Channel) -> Contact:
    """Reuses an existing contact matched by phone/email; otherwise creates a new one from the lead."""
    contact = None
    if fields.get("phone"):
        contact = db.scalar(select(Contact).where(Contact.phone == fields["phone"]))
    if not contact and fields.get("email"):
        contact = db.scalar(select(Contact).where(Contact.email == fields["email"]))
    if contact:
        return contact
    contact = Contact(
        name=fields["name"],
        phone=fields.get("phone"),
        email=fields.get("email"),
        source=channel,
        external_id=leadgen_id,
    )
    db.add(contact)
    db.flush()
    return contact


def _process_leadgen_change(db: Session, settings: Settings, value: dict) -> MetaLeadEvent:
    leadgen_id = value.get("leadgen_id")
    event = MetaLeadEvent(
        leadgen_id=leadgen_id,
        page_id=value.get("page_id"),
        form_id=value.get("form_id"),
        ad_id=value.get("ad_id"),
        raw_payload=json.dumps(value),
    )
    if not settings.meta_page_access_token:
        event.status = "failed"
        event.error = "META_PAGE_ACCESS_TOKEN nije podešen na serveru."
        return event
    try:
        lead_data = fetch_lead_data(leadgen_id, settings.meta_page_access_token, settings.meta_graph_api_version)
        fields = extract_contact_fields(lead_data)
        channel = Channel.instagram if detect_platform(lead_data) == "instagram" else Channel.facebook
        contact = _find_or_create_contact(db, leadgen_id, fields, channel)
        existing_lead = db.scalar(select(Lead).where(Lead.contact_id == contact.id))
        if existing_lead:
            event.status = "duplicate_contact"
            event.contact_id = contact.id
            event.lead_id = existing_lead.id
            return event
        lead = Lead(contact_id=contact.id)
        db.add(lead)
        db.flush()
        event.status = "processed"
        event.contact_id = contact.id
        event.lead_id = lead.id
    except Exception as exc:  # noqa: BLE001 - the webhook must always ack Meta, regardless of the failure cause
        event.status = "failed"
        event.error = str(exc)[:500]
        logger.exception("Obrada Meta lead webhook-a nije uspela (leadgen_id=%s)", leadgen_id)
    return event


@router.post("", status_code=status.HTTP_200_OK)
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Ingests Meta Lead Ads notifications: fetches the full lead and creates a Contact + Lead.

    Meta only cares about getting a 200 back quickly, so every per-lead failure is caught and
    recorded on the MetaLeadEvent row instead of failing the whole request.
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if settings.meta_app_secret and not verify_signature(raw_body, signature, settings.meta_app_secret):
        raise HTTPException(status_code=403, detail="Nevažeći potpis webhook-a.")

    try:
        payload = json.loads(raw_body or b"{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Neispravan JSON.")

    processed = 0
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "leadgen":
                continue
            value = change.get("value", {})
            leadgen_id = value.get("leadgen_id")
            if not leadgen_id:
                continue
            if db.scalar(select(MetaLeadEvent).where(MetaLeadEvent.leadgen_id == leadgen_id)):
                continue
            event = _process_leadgen_change(db, settings, value)
            db.add(event)
            processed += 1

    db.commit()
    return {"processed": processed}
