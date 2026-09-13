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
    google = "google"
    referral = "referral"
    phone = "phone"
    website = "website"


class LeadStage(str, Enum):
    new_inquiry = "new_inquiry"
    contacted = "contacted"
    offer_sent = "offer_sent"
    negotiation = "negotiation"
    waiting_response = "waiting_response"
    deal_won = "deal_won"
    scheduled = "scheduled"
    paid = "paid"
    deal_lost = "deal_lost"
    # Legacy value kept so existing rows stay valid after the pipeline expansion.
    scheduled_paid = "scheduled_paid"


ACTIVE_STAGES = frozenset(
    {
        LeadStage.new_inquiry,
        LeadStage.contacted,
        LeadStage.offer_sent,
        LeadStage.negotiation,
        LeadStage.waiting_response,
    }
)
WON_STAGES = frozenset(
    {LeadStage.deal_won, LeadStage.scheduled, LeadStage.paid, LeadStage.scheduled_paid}
)
LOST_STAGES = frozenset({LeadStage.deal_lost})
FOLLOWUP_STAGES = frozenset(
    {LeadStage.offer_sent, LeadStage.negotiation, LeadStage.waiting_response}
)


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
    owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"), unique=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True, index=True)
    stage: Mapped[LeadStage] = mapped_column(SqlEnum(LeadStage), default=LeadStage.new_inquiry)
    value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lost_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_activity: Mapped[str | None] = mapped_column(String(200), nullable=True)
    next_activity_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    contact: Mapped[Contact] = relationship(back_populates="lead")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="leads")
    proposals: Mapped[list["Proposal"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    activities: Mapped[list["LeadActivity"]] = relationship(back_populates="lead", cascade="all, delete-orphan")


class Proposal(Base, TimestampMixin):
    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    amount: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[str] = mapped_column(String(10), default="RSD")
    items: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="sent")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    lead: Mapped[Lead] = relationship(back_populates="proposals")


class LeadActivity(Base, TimestampMixin):
    __tablename__ = "lead_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)
    type: Mapped[str] = mapped_column(String(30), default="note")
    description: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    lead: Mapped[Lead] = relationship(back_populates="activities")


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


class MetaLeadEvent(Base, TimestampMixin):
    """Audit trail for Meta (Facebook/Instagram) Lead Ads webhook deliveries."""

    __tablename__ = "meta_lead_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    leadgen_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    page_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    form_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ad_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="received")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"), nullable=True)


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
