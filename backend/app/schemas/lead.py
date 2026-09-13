from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.crm import LeadStage


class LeadCreate(BaseModel):
    contact_id: int
    campaign_id: int | None = None
    stage: LeadStage = LeadStage.new_inquiry
    value: int | None = Field(default=None, ge=0)


class LeadUpdate(BaseModel):
    stage: LeadStage
    campaign_id: int | None = Field(default=None)
    value: int | None = Field(default=None, ge=0)


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    campaign_id: int | None
    stage: LeadStage
    value: int | None
    created_at: datetime
    updated_at: datetime
