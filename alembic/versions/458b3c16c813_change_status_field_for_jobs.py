"""change status field for jobs

Revision ID: 458b3c16c813
Revises: 5a5b2a0a8dec, 3b4890df160d
Create Date: 2015-01-17 12:42:14.193286

"""

# revision identifiers, used by Alembic.
revision = '458b3c16c813'
down_revision = ('5a5b2a0a8dec', '3b4890df160d')
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass
