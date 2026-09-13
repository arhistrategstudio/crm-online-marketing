from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Channel, Integration
from app.schemas.integration import IntegrationRead, IntegrationUpdate


router = APIRouter(prefix="/integrations", tags=["Integracije"])
SUPPORTED_CHANNELS = (Channel.facebook, Channel.instagram, Channel.viber, Channel.email)


def ensure_integrations(db: Session) -> None:
    existing = set(db.scalars(select(Integration.channel)))
    missing = [Integration(channel=channel) for channel in SUPPORTED_CHANNELS if channel not in existing]
    if missing:
        db.add_all(missing)
        db.commit()


@router.get("", response_model=list[IntegrationRead])
def list_integrations(db: Session = Depends(get_db)) -> list[Integration]:
    ensure_integrations(db)
    return list(db.scalars(select(Integration).where(Integration.channel.in_(SUPPORTED_CHANNELS))))


@router.put("/{channel}", response_model=IntegrationRead)
def update_integration(channel: Channel, data: IntegrationUpdate, db: Session = Depends(get_db)) -> Integration:
    if channel not in SUPPORTED_CHANNELS:
        raise HTTPException(status_code=422, detail="Nepodržan kanal integracije.")
    ensure_integrations(db)
    integration = db.scalar(select(Integration).where(Integration.channel == channel))
    if not integration:
        raise HTTPException(status_code=404, detail="Integracija nije pronađena.")
    integration.status = data.status
    integration.configuration = data.configuration
    db.commit()
    db.refresh(integration)
    return integration
