"""removing not null constraint

Revision ID: fbdb76ae215
Revises: 12651bdf3b23
Create Date: 2015-02-18 02:00:23.603872

"""

# revision identifiers, used by Alembic.
revision = 'fbdb76ae215'
down_revision = '12651bdf3b23'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('base_user', 'name',
               existing_type=sa.VARCHAR(length=1024),
               nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('base_user', 'name',
               existing_type=sa.VARCHAR(length=1024),
               nullable=False)
    ### end Alembic commands ###