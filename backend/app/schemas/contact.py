from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.crm import Channel


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    source: Channel = Channel.manual
    external_id: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class ContactUpdate(ContactCreate):
    status: str = Field(default="Aktivan", max_length=30)


class ContactRead(ContactUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
