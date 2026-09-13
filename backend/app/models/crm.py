from datetime import date, datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Channel(str, Enum):
    facebook = "facebook"
    instagram = "instagram"
    viber = "viber"
    email = "email"
    manual = "manual"


class LeadStage(str, Enum):
    new_inquiry = "new_inquiry"
    offer_sent = "offer_sent"
    waiting_response = "waiting_response"
    scheduled_paid = "scheduled_paid"


class CampaignStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(50), default="Korisnik")
    status: Mapped[str] = mapped_column(String(30), default="Aktivan")
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(20), default="local")


class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    phone: Mapped[str | None] = mapped_column(String(40), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    source: Mapped[Channel] = mapped_column(SqlEnum(Channel), default=Channel.manual)
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Aktivan")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="contact")
    lead: Mapped["Lead | None"] = relationship(back_populates="contact", uselist=False)


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"), index=True)
    channel: Mapped[Channel] = mapped_column(SqlEnum(Channel))
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unread_count: Mapped[int] = mapped_column(Integer, default=0)
    contact: Mapped[Contact] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)
    sender: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="sent")
    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"), unique=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True, index=True)
    stage: Mapped[LeadStage] = mapped_column(SqlEnum(LeadStage), default=LeadStage.new_inquiry)
    value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contact: Mapped[Contact] = relationship(back_populates="lead")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="leads")


class Integration(Base, TimestampMixin):
    __tablename__ = "integrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel: Mapped[Channel] = mapped_column(SqlEnum(Channel), unique=True)
    status: Mapped[str] = mapped_column(String(30), default="Nije povezano")
    configuration: Mapped[str | None] = mapped_column(Text, nullable=True)


class Meeting(Base, TimestampMixin):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(150))
    start_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact: Mapped["Contact | None"] = relationship()

    @property
    def contact_name(self) -> str | None:
        return self.contact.name if self.contact else None


class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    channel: Mapped[Channel] = mapped_column(SqlEnum(Channel))
    status: Mapped[CampaignStatus] = mapped_column(SqlEnum(CampaignStatus), default=CampaignStatus.draft)
    budget: Mapped[int] = mapped_column(Integer, default=0)
    spend: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[date | None] = mapped_column(nullable=True)
    ended_at: Mapped[date | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    leads: Mapped[list[Lead]] = relationship(back_populates="campaign")
