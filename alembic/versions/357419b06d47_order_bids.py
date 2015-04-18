"""order bids

Revision ID: 357419b06d47
Revises: 574514831e8d
Create Date: 2015-04-19 01:05:41.203745

"""

# revision identifiers, used by Alembic.
revision = '357419b06d47'
down_revision = '574514831e8d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_bid',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('service_provider_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('accepted', sa.Boolean(), nullable=True),
    sa.Column('selected', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['service_provider_id'], ['service_provider.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_bid')
    ### end Alembic commands ###
