"""empty message

Revision ID: 2fba9490b1f4
Revises: 298e7f559106
Create Date: 2015-03-04 22:36:58.886674

"""

# revision identifiers, used by Alembic.
revision = '2fba9490b1f4'
down_revision = '298e7f559106'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('service_provider_skill')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_provider_skill',
    sa.Column('service_provider_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('service_skill_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['service_provider_id'], [u'service_provider.id'], name=u'service_provider_skill_service_provider_id_fkey'),
    sa.ForeignKeyConstraint(['service_skill_id'], [u'service_skill.id'], name=u'service_provider_skill_service_skill_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'service_provider_skill_pkey')
    )
    ### end Alembic commands ###
