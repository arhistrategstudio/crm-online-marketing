from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, CampaignStatus, Lead, LeadStage


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
