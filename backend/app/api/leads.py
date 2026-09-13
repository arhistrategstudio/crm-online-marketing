from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, Contact, Lead
from app.schemas.lead import LeadCreate, LeadRead, LeadUpdate


router = APIRouter(prefix="/leads", tags=["Prodajni levak"])


@router.get("", response_model=list[LeadRead])
def list_leads(db: Session = Depends(get_db)) -> list[Lead]:
    return list(db.scalars(select(Lead).order_by(Lead.updated_at.desc())))


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(data: LeadCreate, db: Session = Depends(get_db)) -> Lead:
    if not db.get(Contact, data.contact_id):
        raise HTTPException(status_code=404, detail="Kontakt nije pronađen.")
    if data.campaign_id is not None and not db.get(Campaign, data.campaign_id):
        raise HTTPException(status_code=404, detail="Kampanja nije pronađena.")
    if db.scalar(select(Lead).where(Lead.contact_id == data.contact_id)):
        raise HTTPException(status_code=409, detail="Lead za ovaj kontakt već postoji.")
    lead = Lead(**data.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.put("/{lead_id}", response_model=LeadRead)
def update_lead(lead_id: int, data: LeadUpdate, db: Session = Depends(get_db)) -> Lead:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nije pronađen.")
    lead.stage = data.stage
    if "value" in data.model_fields_set:
        lead.value = data.value
    if "campaign_id" in data.model_fields_set:
        lead.campaign_id = data.campaign_id
    db.commit()
    db.refresh(lead)
    return lead
