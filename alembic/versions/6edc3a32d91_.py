"""empty message

Revision ID: 6edc3a32d91
Revises: 3609a703337f
Create Date: 2015-01-23 00:36:09.580176

"""

# revision identifiers, used by Alembic.
revision = '6edc3a32d91'
down_revision = '3609a703337f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('signupemail', sa.Column('feedback', sa.String(length=2048), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('signupemail', 'feedback')
    ### end Alembic commands ###