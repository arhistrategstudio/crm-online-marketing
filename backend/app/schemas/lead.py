from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.crm import Channel, LeadStage


class LeadCreate(BaseModel):
    contact_id: int
    campaign_id: int | None = None
    stage: LeadStage = LeadStage.new_inquiry
    value: int | None = Field(default=None, ge=0)
    next_activity: str | None = Field(default=None, max_length=200)
    next_activity_at: datetime | None = None


class LeadUpdate(BaseModel):
    stage: LeadStage | None = None
    campaign_id: int | None = Field(default=None)
    value: int | None = Field(default=None, ge=0)
    lost_reason: str | None = None
    next_activity: str | None = Field(default=None, max_length=200)
    next_activity_at: datetime | None = None
    contact_owner: str | None = Field(default=None, max_length=120)
    contact_notes: str | None = None


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    contact_name: str
    contact_phone: str | None
    contact_email: str | None
    contact_source: Channel
    contact_owner: str | None
    contact_notes: str | None
    campaign_id: int | None
    stage: LeadStage
    value: int | None
    lost_reason: str | None
    next_activity: str | None
    next_activity_at: datetime | None
    followup_due: bool
    proposals_count: int
    last_proposal_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ProposalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    amount: int = Field(default=0, ge=0)
    currency: str = Field(default="RSD", max_length=10)
    items: str | None = None
    notes: str | None = None


class ProposalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    contact_id: int
    title: str
    amount: int
    currency: str
    items: str | None
    notes: str | None
    status: str
    sent_at: datetime | None
    created_at: datetime


class LeadActivityCreate(BaseModel):
    type: str = Field(default="note", max_length=30)
    description: str = Field(min_length=1)
    next_activity: str | None = Field(default=None, max_length=200)
    next_activity_at: datetime | None = None


class LeadActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    type: str
    description: str
    created_by: str | None
    created_at: datetime


class TimelineItem(BaseModel):
    kind: str
    title: str
    detail: str | None = None
    channel: str | None = None
    created_at: datetime
