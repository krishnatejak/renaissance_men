"""making user phone nullable

Revision ID: 15c9834e0b4f
Revises: 3b4890df160d
Create Date: 2015-01-20 00:09:15.533625

"""

# revision identifiers, used by Alembic.
revision = '15c9834e0b4f'
down_revision = '3b4890df160d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'phone',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'phone',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
    ### end Alembic commands ###
