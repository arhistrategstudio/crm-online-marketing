from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Contact, Meeting
from app.schemas.meeting import MeetingCreate, MeetingRead


router = APIRouter(prefix="/meetings", tags=["Sastanci"])


@router.get("", response_model=list[MeetingRead])
def list_meetings(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Meeting]:
    statement = select(Meeting).options(joinedload(Meeting.contact)).order_by(Meeting.start_at)
    if start:
        statement = statement.where(Meeting.end_at >= start)
    if end:
        statement = statement.where(Meeting.start_at <= end)
    return list(db.scalars(statement))


@router.post("", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
def create_meeting(data: MeetingCreate, db: Session = Depends(get_db)) -> Meeting:
    if data.contact_id is not None and not db.get(Contact, data.contact_id):
        raise HTTPException(status_code=404, detail="Kontakt nije pronađen.")
    meeting = Meeting(**data.model_dump())
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)) -> None:
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Sastanak nije pronađen.")
    db.delete(meeting)
    db.commit()
