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
    type: Literal["message", "lead", "reminder"]
    text: str
    reference_id: int
    created_at: datetime


class NotificationFeed(BaseModel):
    count: int
    items: list[NotificationItem]


class LostReasonItem(BaseModel):
    reason: str
    count: int


class DashboardSummary(BaseModel):
    new_inquiries: int
    contacted: int
    active_leads: int
    potential_value: int
    closed_this_month_value: int
    offers_sent: int
    proposals_sent: int
    won: int
    lost: int
    win_rate: float | None
    avg_time_to_sale_days: float | None
    scheduled_paid: int
    campaigns_active: int
    avg_cost_per_lead: float | None
    lost_reasons: list[LostReasonItem]
