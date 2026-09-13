from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, CampaignStatus, Contact, Conversation, Lead, LeadStage
from app.schemas.dashboard import NotificationFeed, NotificationItem, ProspectRead


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict[str, int | float | None]:
    """Returns the MVP dashboard indicators plus campaign efficiency KPIs."""
    def count(stage: LeadStage) -> int:
        return db.scalar(select(func.count()).select_from(Lead).where(Lead.stage == stage)) or 0

    new_inquiries = count(LeadStage.new_inquiry)
    offers_sent = count(LeadStage.offer_sent)
    waiting_response = count(LeadStage.waiting_response)
    scheduled_paid = count(LeadStage.scheduled_paid)

    campaigns_active = db.scalar(
        select(func.count()).select_from(Campaign).where(Campaign.status == CampaignStatus.active)
    ) or 0
    attributed_spend = db.scalar(
        select(func.coalesce(func.sum(Campaign.spend), 0)).where(
            Campaign.status.in_((CampaignStatus.active, CampaignStatus.completed))
        )
    ) or 0
    attributed_leads = db.scalar(
        select(func.count()).select_from(Lead).where(Lead.campaign_id.is_not(None))
    ) or 0
    avg_cost_per_lead = round(attributed_spend / attributed_leads, 2) if attributed_leads else None

    return {
        "new_inquiries": new_inquiries,
        "active_leads": new_inquiries + offers_sent + waiting_response,
        "offers_sent": offers_sent,
        "scheduled_paid": scheduled_paid,
        "campaigns_active": campaigns_active,
        "avg_cost_per_lead": avg_cost_per_lead,
    }


@router.get("/prospects", response_model=list[ProspectRead])
def dashboard_prospects(limit: int = Query(default=5, ge=1, le=20), db: Session = Depends(get_db)) -> list[ProspectRead]:
    """Most recently updated leads, joined with their contact, for the Dashboard prospect list."""
    rows = db.execute(
        select(Lead, Contact)
        .join(Contact, Lead.contact_id == Contact.id)
        .order_by(Lead.updated_at.desc())
        .limit(limit)
    ).all()
    return [
        ProspectRead(
            lead_id=lead.id,
            contact_id=contact.id,
            name=contact.name,
            stage=lead.stage,
            value=lead.value,
            updated_at=lead.updated_at,
        )
        for lead, contact in rows
    ]


@router.get("/notifications", response_model=NotificationFeed)
def dashboard_notifications(db: Session = Depends(get_db)) -> NotificationFeed:
    """Computed, real-time notification feed: unread conversations + new inquiries. Not persisted."""
    unread_rows = db.execute(
        select(Conversation, Contact)
        .join(Contact, Conversation.contact_id == Contact.id)
        .where(Conversation.unread_count > 0)
        .order_by(Conversation.created_at.desc())
    ).all()
    new_lead_rows = db.execute(
        select(Lead, Contact)
        .join(Contact, Lead.contact_id == Contact.id)
        .where(Lead.stage == LeadStage.new_inquiry)
        .order_by(Lead.created_at.desc())
        .limit(5)
    ).all()

    items = [
        NotificationItem(
            type="message",
            text=f"{contact.name}: {conversation.unread_count} nova poruka(e)",
            reference_id=conversation.id,
            created_at=conversation.created_at,
        )
        for conversation, contact in unread_rows
    ] + [
        NotificationItem(
            type="lead",
            text=f"Novi upit: {contact.name}",
            reference_id=lead.id,
            created_at=lead.created_at,
        )
        for lead, contact in new_lead_rows
    ]
    items.sort(key=lambda item: item.created_at, reverse=True)
    return NotificationFeed(count=len(items), items=items[:10])
