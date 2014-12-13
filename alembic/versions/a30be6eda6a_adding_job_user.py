"""adding job,user

Revision ID: a30be6eda6a
Revises: 5f691302544
Create Date: 2014-12-13 21:07:59.212672

"""

# revision identifiers, used by Alembic.
revision = 'a30be6eda6a'
down_revision = '5f691302544'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_type', sa.Enum('admin', 'user', name='user_types'), nullable=True),
    sa.Column('name', sa.String(length=1024), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('location', postgresql.ARRAY(sa.Float(), dimensions=1), nullable=True),
    sa.Column('password', sa.String(length=80), nullable=True),
    sa.Column('address', sa.String(length=2048), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('job',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('assigned', 'quoted', 'started', 'complete', name='status_types'), nullable=True),
    sa.Column('service_provider_id', sa.Integer(), nullable=True),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('location', postgresql.ARRAY(sa.Float(), dimensions=1), nullable=True),
    sa.Column('request', sa.String(length=2048), nullable=True),
    sa.Column('inspection', sa.Boolean(), nullable=True),
    sa.Column('appointment_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('quote', sa.Float(), nullable=True),
    sa.Column('quoted_duration', sa.Float(), nullable=True),
    sa.Column('started', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ended', sa.DateTime(timezone=True), nullable=True),
    sa.Column('materials_required', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.ForeignKeyConstraint(['service_provider_id'], ['service_provider.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('job')
    op.drop_table('user')
    ### end Alembic commands ###
