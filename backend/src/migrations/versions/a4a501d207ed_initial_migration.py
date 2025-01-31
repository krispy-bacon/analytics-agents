"""Initial database migration.

Revision ID: a4a501d207ed
Revises: 
Create Date: 2024-01-31 20:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'a4a501d207ed'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create datasets table
    op.create_table(
        'datasets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('schema', postgresql.JSONB(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_datasets_id'), 'datasets', ['id'], unique=False)

    # Create data_points table
    op.create_table(
        'data_points',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dataset_id', sa.Integer(), nullable=False),
        sa.Column('row_index', sa.Integer(), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_points_id'), 'data_points', ['id'], unique=False)
    op.create_index(op.f('ix_data_points_dataset_id'), 'data_points', ['dataset_id'], unique=False)
    op.create_index(op.f('ix_data_points_row_index'), 'data_points', ['row_index'], unique=False)

    # Create upload_sessions table
    op.create_table(
        'upload_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dataset_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('total_chunks', sa.Integer(), nullable=True),
        sa.Column('chunks_received', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_upload_sessions_id'), 'upload_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_upload_sessions_dataset_id'), 'upload_sessions', ['dataset_id'], unique=False)

def downgrade() -> None:
    op.drop_table('upload_sessions')
    op.drop_table('data_points')
    op.drop_table('datasets') 