""" Init

Revision ID: 28f7cedaa9db
Revises:
Create Date: 2022-04-09 05:24:31.160446

"""
from datetime import datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "28f7cedaa9db"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    status = sa.Enum("pending", "running", "done", "failed", name="job_state")
    op.create_table(
        "job",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_uuid", sa.Text(), nullable=True),
        sa.Column("status", status, nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), default=datetime.utcnow, nullable=False),
        sa.Column("updated_at", sa.DateTime(), default=None, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint("id"),
        keep_existing=True,
    )
    pass


def downgrade():
    op.drop_table("job")
    pass
