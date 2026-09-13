from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.models.crm import LeadStage


class ProspectRead(BaseModel):
    lead_id: int
    contact_id: int
    name: str
    stage: LeadStage
    value: int | None
    updated_at: datetime


class NotificationItem(BaseModel):
    type: Literal["message", "lead"]
    text: str
    reference_id: int
    created_at: datetime


class NotificationFeed(BaseModel):
    count: int
    items: list[NotificationItem]
