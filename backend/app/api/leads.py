from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import (
    FOLLOWUP_STAGES,
    LOST_STAGES,
    WON_STAGES,
    Campaign,
    Contact,
    Conversation,
    Lead,
    LeadActivity,
    LeadStage,
    Message,
    Proposal,
)
from app.schemas.lead import (
    LeadActivityCreate,
    LeadActivityRead,
    LeadCreate,
    LeadRead,
    LeadUpdate,
    ProposalCreate,
    ProposalRead,
    TimelineItem,
)


router = APIRouter(prefix="/leads", tags=["Prodajni levak"])

FOLLOWUP_DAYS = 3


def _lead_read(lead: Lead, contact: Contact) -> LeadRead:
    proposals = sorted(lead.proposals, key=lambda p: p.sent_at or p.created_at)
    last_proposal_at = (proposals[-1].sent_at or proposals[-1].created_at) if proposals else None
    base = last_proposal_at or lead.updated_at
    followup_due = bool(
        lead.stage in FOLLOWUP_STAGES and base and (datetime.now() - base).days >= FOLLOWUP_DAYS
    )
    return LeadRead(
        id=lead.id,
        contact_id=lead.contact_id,
        contact_name=contact.name,
        contact_phone=contact.phone,
        contact_email=contact.email,
        contact_source=contact.source,
        contact_owner=contact.owner,
        contact_notes=contact.notes,
        campaign_id=lead.campaign_id,
        stage=lead.stage,
        value=lead.value,
        lost_reason=lead.lost_reason,
        next_activity=lead.next_activity,
        next_activity_at=lead.next_activity_at,
        followup_due=followup_due,
        proposals_count=len(proposals),
        last_proposal_at=last_proposal_at,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


def _lead_or_404(db: Session, lead_id: int) -> Lead:
    lead = db.scalar(
        select(Lead).options(selectinload(Lead.proposals)).where(Lead.id == lead_id)
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nije pronađen.")
    return lead


def _log_activity(db: Session, lead_id: int, activity_type: str, description: str) -> None:
    db.add(LeadActivity(lead_id=lead_id, type=activity_type, description=description))


@router.get("", response_model=list[LeadRead])
def list_leads(db: Session = Depends(get_db)) -> list[LeadRead]:
    rows = db.execute(
        select(Lead, Contact)
        .options(selectinload(Lead.proposals))
        .join(Contact, Lead.contact_id == Contact.id)
        .order_by(Lead.updated_at.desc())
    ).all()
    return [_lead_read(lead, contact) for lead, contact in rows]


@router.get("/followups", response_model=list[LeadRead])
def list_followups(
    days: int = Query(default=FOLLOWUP_DAYS, ge=1, le=60),
    db: Session = Depends(get_db),
) -> list[LeadRead]:
    """Leads where a proposal was sent and there has been no response for `days` days."""
    cutoff = datetime.now() - timedelta(days=days)
    rows = db.execute(
        select(Lead, Contact)
        .options(selectinload(Lead.proposals))
        .join(Contact, Lead.contact_id == Contact.id)
        .where(Lead.stage.in_(FOLLOWUP_STAGES))
        .order_by(Lead.updated_at.asc())
    ).all()
    result: list[LeadRead] = []
    for lead, contact in rows:
        last_proposal_at = max(
            (p.sent_at or p.created_at for p in lead.proposals), default=None
        )
        base = last_proposal_at or lead.updated_at
        if base and base <= cutoff:
            result.append(_lead_read(lead, contact))
    return result


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(data: LeadCreate, db: Session = Depends(get_db)) -> LeadRead:
    contact = db.get(Contact, data.contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nije pronađen.")
    if data.campaign_id is not None and not db.get(Campaign, data.campaign_id):
        raise HTTPException(status_code=404, detail="Kampanja nije pronađena.")
    if db.scalar(select(Lead).where(Lead.contact_id == data.contact_id)):
        raise HTTPException(status_code=409, detail="Lead za ovaj kontakt već postoji.")
    lead = Lead(**data.model_dump())
    db.add(lead)
    db.flush()
    _log_activity(db, lead.id, "note", "Lead je kreiran u prodajnom levku.")
    db.commit()
    db.refresh(lead)
    return _lead_read(lead, contact)


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: int, db: Session = Depends(get_db)) -> LeadRead:
    lead = _lead_or_404(db, lead_id)
    return _lead_read(lead, lead.contact)


@router.put("/{lead_id}", response_model=LeadRead)
def update_lead(lead_id: int, data: LeadUpdate, db: Session = Depends(get_db)) -> LeadRead:
    lead = _lead_or_404(db, lead_id)
    fields = data.model_fields_set
    if "stage" in fields and data.stage is not None and data.stage != lead.stage:
        _log_activity(
            db,
            lead.id,
            "stage_change",
            f"Faza promenjena: {lead.stage.value} → {data.stage.value}",
        )
        lead.stage = data.stage
    if "value" in fields:
        lead.value = data.value
    if "campaign_id" in fields:
        lead.campaign_id = data.campaign_id
    if "lost_reason" in fields:
        lead.lost_reason = data.lost_reason
    if "next_activity" in fields:
        lead.next_activity = data.next_activity
    if "next_activity_at" in fields:
        lead.next_activity_at = data.next_activity_at
    if "contact_owner" in fields:
        lead.contact.owner = data.contact_owner
    if "contact_notes" in fields:
        lead.contact.notes = data.contact_notes
    db.commit()
    db.refresh(lead)
    return _lead_read(lead, lead.contact)


@router.get("/{lead_id}/activities", response_model=list[LeadActivityRead])
def list_activities(lead_id: int, db: Session = Depends(get_db)) -> list[LeadActivity]:
    _lead_or_404(db, lead_id)
    return list(
        db.scalars(
            select(LeadActivity)
            .where(LeadActivity.lead_id == lead_id)
            .order_by(LeadActivity.created_at.desc())
        )
    )


@router.post(
    "/{lead_id}/activities",
    response_model=LeadActivityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    lead_id: int, data: LeadActivityCreate, db: Session = Depends(get_db)
) -> LeadActivity:
    lead = _lead_or_404(db, lead_id)
    activity = LeadActivity(lead_id=lead_id, type=data.type, description=data.description)
    db.add(activity)
    if data.next_activity is not None:
        lead.next_activity = data.next_activity
    if data.next_activity_at is not None:
        lead.next_activity_at = data.next_activity_at
    db.commit()
    db.refresh(activity)
    return activity


@router.get("/{lead_id}/proposals", response_model=list[ProposalRead])
def list_proposals(lead_id: int, db: Session = Depends(get_db)) -> list[Proposal]:
    _lead_or_404(db, lead_id)
    return list(
        db.scalars(
            select(Proposal)
            .where(Proposal.lead_id == lead_id)
            .order_by(Proposal.created_at.desc())
        )
    )


@router.post(
    "/{lead_id}/proposals",
    response_model=ProposalRead,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal(
    lead_id: int, data: ProposalCreate, db: Session = Depends(get_db)
) -> Proposal:
    lead = _lead_or_404(db, lead_id)
    proposal = Proposal(
        lead_id=lead_id,
        contact_id=lead.contact_id,
        title=data.title,
        amount=data.amount,
        currency=data.currency,
        items=data.items,
        notes=data.notes,
        status="sent",
        sent_at=datetime.now(),
    )
    db.add(proposal)
    _log_activity(
        db,
        lead.id,
        "proposal",
        f"Ponuda poslata: {data.title} — {data.amount} {data.currency}",
    )
    if lead.stage not in FOLLOWUP_STAGES and lead.stage not in WON_STAGES and lead.stage not in LOST_STAGES:
        lead.stage = LeadStage.offer_sent
    lead.next_activity = "Follow-up provera ponude"
    lead.next_activity_at = datetime.now() + timedelta(days=FOLLOWUP_DAYS)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.get("/{lead_id}/history", response_model=list[TimelineItem])
def lead_history(lead_id: int, db: Session = Depends(get_db)) -> list[TimelineItem]:
    """Full communication history: messages, stage changes, notes and proposals."""
    lead = _lead_or_404(db, lead_id)
    contact_id = lead.contact_id

    message_rows = db.execute(
        select(Message, Conversation)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.contact_id == contact_id)
        .order_by(Message.created_at.asc())
    ).all()
    items = [
        TimelineItem(
            kind="message",
            title="Dolazna poruka" if message.sender != "agent" else "Poslata poruka",
            detail=message.content,
            channel=conversation.channel.value,
            created_at=message.created_at,
        )
        for message, conversation in message_rows
    ]
    items += [
        TimelineItem(
            kind="activity",
            title=activity.type,
            detail=activity.description,
            created_at=activity.created_at,
        )
        for activity in db.scalars(
            select(LeadActivity).where(LeadActivity.lead_id == lead_id)
        )
    ]
    items += [
        TimelineItem(
            kind="proposal",
            title=f"Ponuda: {proposal.title}",
            detail=f"{proposal.amount} {proposal.currency}",
            created_at=proposal.sent_at or proposal.created_at,
        )
        for proposal in db.scalars(select(Proposal).where(Proposal.lead_id == lead_id))
    ]
    items.sort(key=lambda item: item.created_at)
    return items
