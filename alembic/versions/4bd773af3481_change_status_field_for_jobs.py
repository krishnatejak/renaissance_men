"""change status field for jobs

Revision ID: 4bd773af3481
Revises: 458b3c16c813, 6edc3a32d91
Create Date: 2015-01-31 17:23:04.024452

"""

# revision identifiers, used by Alembic.
revision = '4bd773af3481'
down_revision = ('458b3c16c813', '6edc3a32d91')
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass
