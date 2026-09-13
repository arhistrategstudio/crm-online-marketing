"""expand leads (stages, reminders, proposals, activities)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_CHANNELS = ['google', 'referral', 'phone', 'website']
NEW_STAGES = ['contacted', 'negotiation', 'deal_won', 'scheduled', 'paid', 'deal_lost']


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        # Native PostgreSQL enums must be extended before new values can be stored.
        for value in NEW_CHANNELS:
            op.execute(f"ALTER TYPE channel ADD VALUE IF NOT EXISTS '{value}'")
        for value in NEW_STAGES:
            op.execute(f"ALTER TYPE leadstage ADD VALUE IF NOT EXISTS '{value}'")

    op.add_column('contacts', sa.Column('owner', sa.String(length=120), nullable=True))
    op.add_column('leads', sa.Column('lost_reason', sa.Text(), nullable=True))
    op.add_column('leads', sa.Column('next_activity', sa.String(length=200), nullable=True))
    op.add_column('leads', sa.Column('next_activity_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_leads_next_activity_at'), 'leads', ['next_activity_at'], unique=False)
    op.add_column(
        'messages',
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'proposals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('items', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id']),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_proposals_lead_id'), 'proposals', ['lead_id'], unique=False)
    op.create_index(op.f('ix_proposals_contact_id'), 'proposals', ['contact_id'], unique=False)

    op.create_table(
        'lead_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=30), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_by', sa.String(length=120), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_lead_activities_lead_id'), 'lead_activities', ['lead_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_lead_activities_lead_id'), table_name='lead_activities')
    op.drop_table('lead_activities')
    op.drop_index(op.f('ix_proposals_contact_id'), table_name='proposals')
    op.drop_index(op.f('ix_proposals_lead_id'), table_name='proposals')
    op.drop_table('proposals')
    op.drop_column('messages', 'created_at')
    op.drop_index(op.f('ix_leads_next_activity_at'), table_name='leads')
    op.drop_column('leads', 'next_activity_at')
    op.drop_column('leads', 'next_activity')
    op.drop_column('leads', 'lost_reason')
    op.drop_column('contacts', 'owner')
