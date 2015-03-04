"""empty message

Revision ID: 4991625194b6
Revises: 10b3162f8cc6
Create Date: 2015-03-04 23:03:38.324523

"""

# revision identifiers, used by Alembic.
revision = '4991625194b6'
down_revision = '10b3162f8cc6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_provider_skill', sa.Column('trash', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service_provider_skill', 'trash')
    ### end Alembic commands ###
