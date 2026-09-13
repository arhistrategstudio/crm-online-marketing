from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Campaign, WON_STAGES
from app.schemas.campaign import CampaignCreate, CampaignRead, CampaignUpdate


router = APIRouter(prefix="/campaigns", tags=["Kampanje"])


def serialize_campaign(campaign: Campaign) -> CampaignRead:
    """Adds derived KPI fields (leads_count, cost_per_lead, conversion_rate) on top of stored columns."""
    leads = campaign.leads
    leads_count = len(leads)
    cost_per_lead = round(campaign.spend / leads_count, 2) if leads_count else None
    won_count = sum(1 for lead in leads if lead.stage in WON_STAGES)
    conversion_rate = round(won_count / leads_count * 100, 1) if leads_count else None
    return CampaignRead.model_validate(
        {
            "id": campaign.id,
            "name": campaign.name,
            "channel": campaign.channel,
            "status": campaign.status,
            "budget": campaign.budget,
            "spend": campaign.spend,
            "started_at": campaign.started_at,
            "ended_at": campaign.ended_at,
            "notes": campaign.notes,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
            "leads_count": leads_count,
            "cost_per_lead": cost_per_lead,
            "conversion_rate": conversion_rate,
        }
    )


def get_campaign_or_404(db: Session, campaign_id: int) -> Campaign:
    campaign = db.scalar(
        select(Campaign).options(selectinload(Campaign.leads)).where(Campaign.id == campaign_id)
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Kampanja nije pronađena.")
    return campaign


@router.get("", response_model=list[CampaignRead])
def list_campaigns(db: Session = Depends(get_db)) -> list[CampaignRead]:
    statement = select(Campaign).options(selectinload(Campaign.leads)).order_by(Campaign.created_at.desc())
    return [serialize_campaign(campaign) for campaign in db.scalars(statement)]


@router.post("", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(data: CampaignCreate, db: Session = Depends(get_db)) -> CampaignRead:
    campaign = Campaign(**data.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return serialize_campaign(get_campaign_or_404(db, campaign.id))


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)) -> CampaignRead:
    return serialize_campaign(get_campaign_or_404(db, campaign_id))


@router.put("/{campaign_id}", response_model=CampaignRead)
def update_campaign(campaign_id: int, data: CampaignUpdate, db: Session = Depends(get_db)) -> CampaignRead:
    campaign = get_campaign_or_404(db, campaign_id)
    for field, value in data.model_dump().items():
        setattr(campaign, field, value)
    db.commit()
    db.refresh(campaign)
    return serialize_campaign(get_campaign_or_404(db, campaign_id))


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)) -> None:
    campaign = get_campaign_or_404(db, campaign_id)
    db.delete(campaign)
    db.commit()
