from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MeetingCreate(BaseModel):
    contact_id: int | None = None
    title: str = Field(min_length=1, max_length=150)
    start_at: datetime
    end_at: datetime
    notes: str | None = None

    @model_validator(mode="after")
    def check_times(self) -> "MeetingCreate":
        if self.end_at <= self.start_at:
            raise ValueError("Vreme završetka mora biti posle vremena početka.")
        return self


class MeetingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int | None
    contact_name: str | None
    title: str
    start_at: datetime
    end_at: datetime
    notes: str | None
    created_at: datetime
    updated_at: datetime
