from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.crm import Channel


class IntegrationUpdate(BaseModel):
    status: str = Field(pattern="^(Nije povezano|Povezano|Greška)$")
    configuration: str | None = None


class IntegrationRead(IntegrationUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel: Channel
    created_at: datetime
    updated_at: datetime
