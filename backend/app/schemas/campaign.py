from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.crm import CampaignStatus, Channel


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    channel: Channel
    status: CampaignStatus = CampaignStatus.draft
    budget: int = Field(default=0, ge=0)
    spend: int = Field(default=0, ge=0)
    started_at: date | None = None
    ended_at: date | None = None
    notes: str | None = None


class CampaignUpdate(CampaignCreate):
    pass


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    channel: Channel
    status: CampaignStatus
    budget: int
    spend: int
    started_at: date | None
    ended_at: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    leads_count: int = 0
    cost_per_lead: float | None = None
    conversion_rate: float | None = None
