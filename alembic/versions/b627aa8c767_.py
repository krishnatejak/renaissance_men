"""empty message

Revision ID: b627aa8c767
Revises: 45a2f632b3b9
Create Date: 2015-04-07 01:59:35.345093

"""

# revision identifiers, used by Alembic.
revision = 'b627aa8c767'
down_revision = '45a2f632b3b9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('missedorders', sa.Column('service_available', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('missedorders', 'service_available')
    ### end Alembic commands ###
