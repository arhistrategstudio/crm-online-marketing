from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    ACTIVE_STAGES,
    LOST_STAGES,
    WON_STAGES,
    Campaign,
    CampaignStatus,
    Contact,
    Conversation,
    Lead,
    LeadStage,
    Proposal,
)
from app.schemas.dashboard import (
    DashboardSummary,
    LostReasonItem,
    NotificationFeed,
    NotificationItem,
    ProspectRead,
)


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _count_by_stages(db: Session, stages) -> int:
    return db.scalar(select(func.count()).select_from(Lead).where(Lead.stage.in_(stages))) or 0


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    """Dashboard indicators, sales funnel value and conversion statistics."""
    new_inquiries = _count_by_stages(db, {LeadStage.new_inquiry})
    contacted = _count_by_stages(db, {LeadStage.contacted})
    active_leads = _count_by_stages(db, ACTIVE_STAGES)
    won = _count_by_stages(db, WON_STAGES)
    lost = _count_by_stages(db, LOST_STAGES)

    potential_value = db.scalar(
        select(func.coalesce(func.sum(Lead.value), 0)).where(Lead.stage.in_(ACTIVE_STAGES))
    ) or 0

    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    closed_this_month_value = db.scalar(
        select(func.coalesce(func.sum(Lead.value), 0)).where(
            Lead.stage.in_(WON_STAGES), Lead.updated_at >= month_start
        )
    ) or 0

    proposals_sent = db.scalar(select(func.count()).select_from(Proposal)) or 0
    offers_sent = _count_by_stages(db, {LeadStage.offer_sent})
    scheduled_paid = _count_by_stages(db, WON_STAGES)

    closed = won + lost
    win_rate = round(won / closed * 100, 1) if closed else None

    won_rows = db.scalars(select(Lead).where(Lead.stage.in_(WON_STAGES))).all()
    if won_rows:
        avg_time_to_sale_days = round(
            sum((lead.updated_at - lead.created_at).total_seconds() for lead in won_rows)
            / len(won_rows)
            / 86400,
            1,
        )
    else:
        avg_time_to_sale_days = None

    lost_rows = db.execute(
        select(Lead.lost_reason, func.count())
        .where(Lead.stage.in_(LOST_STAGES))
        .group_by(Lead.lost_reason)
    ).all()
    lost_reasons = [
        LostReasonItem(reason=reason or "Nije naveden", count=count)
        for reason, count in sorted(lost_rows, key=lambda row: row[1], reverse=True)
    ]

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

    return DashboardSummary(
        new_inquiries=new_inquiries,
        contacted=contacted,
        active_leads=active_leads,
        potential_value=potential_value,
        closed_this_month_value=closed_this_month_value,
        offers_sent=offers_sent,
        proposals_sent=proposals_sent,
        won=won,
        lost=lost,
        win_rate=win_rate,
        avg_time_to_sale_days=avg_time_to_sale_days,
        scheduled_paid=scheduled_paid,
        campaigns_active=campaigns_active,
        avg_cost_per_lead=avg_cost_per_lead,
        lost_reasons=lost_reasons,
    )


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
    """Computed, real-time notification feed: unread conversations, new inquiries and reminders."""
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
    reminder_rows = db.execute(
        select(Lead, Contact)
        .join(Contact, Lead.contact_id == Contact.id)
        .where(Lead.next_activity_at.is_not(None), Lead.next_activity_at <= datetime.now())
        .order_by(Lead.next_activity_at.asc())
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
    ] + [
        NotificationItem(
            type="reminder",
            text=f"Podsetnik: {lead.next_activity or 'aktivnost'} — {contact.name}",
            reference_id=lead.id,
            created_at=lead.next_activity_at or datetime.now(),
        )
        for lead, contact in reminder_rows
    ]
    items.sort(key=lambda item: item.created_at, reverse=True)
    return NotificationFeed(count=len(items), items=items[:10])
