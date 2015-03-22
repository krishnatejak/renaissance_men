"""order to orders

Revision ID: 876c88b037d
Revises: 9cc96c394e6
Create Date: 2015-03-21 17:09:16.366767

"""

# revision identifiers, used by Alembic.
revision = '876c88b037d'
down_revision = '9cc96c394e6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('service', sa.String(length=256), nullable=True),
    sa.Column('location', pg.ARRAY(sa.Float(), dimensions=1), nullable=True),
    sa.Column('status', sa.Enum('created', 'processing', 'assigned', 'completed', name='orders_status_types'), nullable=True),
    sa.Column('request', sa.String(length=2048), nullable=True),
    sa.Column('scheduled', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed', sa.DateTime(timezone=True), nullable=True),
    sa.Column('address', sa.String(length=2048), nullable=True),
    sa.Column('service_user_id', sa.Integer(), nullable=True),
    sa.Column('service_provider_id', sa.Integer(), nullable=True),
    sa.Column('job_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['job_id'], ['job.id'], ),
    sa.ForeignKeyConstraint(['service_provider_id'], ['service_provider.id'], ),
    sa.ForeignKeyConstraint(['service_user_id'], ['service_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('details', pg.JSON(none_as_null=True), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('event')
    op.drop_table('order')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order',
    sa.Column('id', sa.INTEGER(), server_default=sa.text(u"nextval('order_id_seq'::regclass)"), nullable=False),
    sa.Column('service', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('location', pg.ARRAY(pg.DOUBLE_PRECISION(precision=53)), autoincrement=False, nullable=True),
    sa.Column('status', pg.ENUM(u'created', u'processing', u'assigned', u'completed', name='order_status_types'), autoincrement=False, nullable=True),
    sa.Column('request', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('scheduled', pg.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('created', pg.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('completed', pg.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('service_user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('service_provider_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('job_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['job_id'], [u'job.id'], name=u'order_job_id_fkey'),
    sa.ForeignKeyConstraint(['service_provider_id'], [u'service_provider.id'], name=u'order_service_provider_id_fkey'),
    sa.ForeignKeyConstraint(['service_user_id'], [u'service_user.id'], name=u'order_service_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'order_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('event',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('start_time', pg.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('end_time', pg.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('order_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('trash', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['order_id'], [u'order.id'], name=u'event_order_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'event_pkey')
    )
    op.drop_table('order_details')
    op.drop_table('orders')
    ### end Alembic commands ###
