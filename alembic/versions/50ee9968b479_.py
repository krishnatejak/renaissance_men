"""empty message

Revision ID: 50ee9968b479
Revises: b627aa8c767
Create Date: 2015-04-07 02:39:31.180114

"""

# revision identifiers, used by Alembic.
revision = '50ee9968b479'
down_revision = 'b627aa8c767'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('location_permitted', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'location_permitted')
    ### end Alembic commands ###