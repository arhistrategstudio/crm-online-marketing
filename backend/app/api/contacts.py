from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Contact
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate


router = APIRouter(prefix="/contacts", tags=["Kontakti"])


def find_existing_contact(db: Session, data: ContactCreate) -> Contact | None:
    """Prevents duplicates with the requested matching priority."""
    if data.external_id:
        contact = db.scalar(select(Contact).where(Contact.external_id == data.external_id))
        if contact:
            return contact
    if data.phone:
        contact = db.scalar(select(Contact).where(Contact.phone == data.phone))
        if contact:
            return contact
    if data.email:
        return db.scalar(select(Contact).where(Contact.email == str(data.email)))
    return None


@router.get("", response_model=list[ContactRead])
def list_contacts(
    search: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
) -> list[Contact]:
    statement = select(Contact).order_by(Contact.created_at.desc())
    if search:
        term = f"%{search}%"
        statement = statement.where(or_(Contact.name.ilike(term), Contact.email.ilike(term), Contact.phone.ilike(term)))
    return list(db.scalars(statement))


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(data: ContactCreate, db: Session = Depends(get_db)) -> Contact:
    if find_existing_contact(db, data):
        raise HTTPException(status_code=409, detail="Kontakt već postoji.")
    contact = Contact(**data.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(contact_id: int, db: Session = Depends(get_db)) -> Contact:
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nije pronađen.")
    return contact


@router.put("/{contact_id}", response_model=ContactRead)
def update_contact(contact_id: int, data: ContactUpdate, db: Session = Depends(get_db)) -> Contact:
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nije pronađen.")
    for field, value in data.model_dump().items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact
