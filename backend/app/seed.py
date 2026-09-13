"""Controlled development data. Run with: python -m app.seed"""

from sqlalchemy import select

from app.database import SessionLocal, engine
from app.models import Base, Campaign, CampaignStatus, Channel, Contact, Conversation, Lead, LeadStage, Message, User
from app.security import hash_password


DEMO_USER_EMAIL = "demo@crm.rs"
DEMO_USER_PASSWORD = "demo1234"

CONTACTS = [
    ("Ana Jovanović", "064 123 4567", "ana@primer.rs", Channel.instagram),
    ("Marko Petrović", "065 222 111", "marko@primer.rs", Channel.facebook),
    ("Jelena Ilić", "063 345 678", "jelena@primer.rs", Channel.email),
    ("Nikola Savić", "064 777 888", "nikola@primer.rs", Channel.viber),
    ("Milica Pavlović", "062 901 234", "milica@primer.rs", Channel.instagram),
    ("Stefan Marković", "064 555 098", "stefan@primer.rs", Channel.facebook),
    ("Teodora Stanić", "061 444 222", "teodora@primer.rs", Channel.email),
    ("Luka Đorđević", "065 900 123", "luka@primer.rs", Channel.viber),
]

CAMPAIGNS = [
    ("Prolećna akcija - Instagram", Channel.instagram, CampaignStatus.active, 60000, 32000),
    ("Facebook lokalna ponuda", Channel.facebook, CampaignStatus.active, 45000, 41000),
    ("Viber podsetnik kupcima", Channel.viber, CampaignStatus.completed, 15000, 15000),
    ("Instagram retargeting", Channel.instagram, CampaignStatus.paused, 30000, 12000),
    ("Facebook nova kolekcija", Channel.facebook, CampaignStatus.draft, 50000, 0),
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.scalar(select(User).where(User.email == DEMO_USER_EMAIL)):
            db.add(User(name="Demo vlasnik", email=DEMO_USER_EMAIL, password_hash=hash_password(DEMO_USER_PASSWORD), auth_provider="local", role="Vlasnik"))
            db.commit()

        existing_campaign_names = set(db.scalars(select(Campaign.name)))
        missing_campaigns = [Campaign(name=name, channel=channel, status=status, budget=budget, spend=spend) for name, channel, status, budget, spend in CAMPAIGNS if name not in existing_campaign_names]
        if missing_campaigns:
            db.add_all(missing_campaigns)
            db.commit()
        campaigns = list(db.scalars(select(Campaign).order_by(Campaign.id)))

        existing_emails = set(db.scalars(select(Contact.email)))
        missing_contacts = [Contact(name=name, phone=phone, email=email, source=channel) for name, phone, email, channel in CONTACTS if email not in existing_emails]
        if missing_contacts:
            db.add_all(missing_contacts)
            db.commit()
        contacts = list(db.scalars(select(Contact).order_by(Contact.id)))

        if not db.scalar(select(Conversation)):
            channels = [Channel.instagram, Channel.facebook, Channel.email, Channel.viber]
            conversations = [Conversation(contact_id=contact.id, channel=channels[index % 4], unread_count=1 if index < 3 else 0) for index, contact in enumerate(contacts[:8])]
            conversations.extend([Conversation(contact_id=contacts[0].id, channel=Channel.instagram), Conversation(contact_id=contacts[1].id, channel=Channel.facebook)])
            db.add_all(conversations)
            db.flush()
            text = ["Zdravo, interesuje me ponuda.", "Hvala na upitu.", "Da li je dostava dostupna?", "Naravno, poslaćemo detalje danas.", "Kada mogu da očekujem odgovor?"]
            db.add_all([Message(conversation_id=conversations[index % len(conversations)].id, sender="customer" if index % 2 == 0 else "agent", content=text[index % len(text)]) for index in range(25)])

        if not db.scalar(select(Lead)):
            stages = [LeadStage.new_inquiry, LeadStage.offer_sent, LeadStage.waiting_response, LeadStage.scheduled_paid]
            db.add_all(
                [
                    Lead(contact_id=contact.id, campaign_id=campaigns[index % len(campaigns)].id, stage=stages[index % 4], value=(index + 1) * 10000)
                    for index, contact in enumerate(contacts[:4])
                ]
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
