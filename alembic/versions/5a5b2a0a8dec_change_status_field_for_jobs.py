"""change status field for jobs

Revision ID: 5a5b2a0a8dec
Revises: 28161fcf0f3e
Create Date: 2015-01-05 16:27:28.903595

"""

# revision identifiers, used by Alembic.
revision = '5a5b2a0a8dec'
down_revision = '28161fcf0f3e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("job", "status", type_=sa.Enum('assigned', 'accepted', 'rejected', 'started', 'complete', name='status_types'), nullable=True)
    pass


def downgrade():
    pass
