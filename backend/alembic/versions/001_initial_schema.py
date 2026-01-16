"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create transcripts table
    op.create_table(
        'transcripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('game_date', sa.Date(), nullable=True),
        sa.Column('sport', sa.String(100), nullable=True),
        sa.Column('teams', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('commentators', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('processed', sa.Boolean(), default=False),
        sa.Column('word_count', sa.String(50), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
    )

    # Create players table
    op.create_table(
        'players',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('aliases', postgresql.ARRAY(sa.String()), default=list),
        sa.Column('team', sa.String(255), nullable=True),
        sa.Column('sport', sa.String(100), nullable=True),
        sa.Column('position', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Create analysis_results table
    op.create_table(
        'analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('transcript_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcripts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('sentiment_label', sa.String(20), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('mention_count', sa.Integer(), default=0),
        sa.Column('adjectives', postgresql.JSONB(), default=list),
        sa.Column('phrases', postgresql.JSONB(), default=list),
        sa.Column('excerpts', postgresql.JSONB(), default=list),
        sa.Column('analyzed_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Create indexes
    op.create_index('ix_transcripts_sport', 'transcripts', ['sport'])
    op.create_index('ix_transcripts_processed', 'transcripts', ['processed'])
    op.create_index('ix_players_name', 'players', ['name'])
    op.create_index('ix_players_sport', 'players', ['sport'])
    op.create_index('ix_analysis_results_transcript_id', 'analysis_results', ['transcript_id'])
    op.create_index('ix_analysis_results_player_id', 'analysis_results', ['player_id'])


def downgrade() -> None:
    op.drop_table('analysis_results')
    op.drop_table('players')
    op.drop_table('transcripts')
