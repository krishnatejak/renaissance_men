"""removing service_provider_id for service_skill

Revision ID: 2d71cc6b2b18
Revises: cff1d3443a0
Create Date: 2015-02-07 12:42:41.818977

"""

# revision identifiers, used by Alembic.
revision = '2d71cc6b2b18'
down_revision = 'cff1d3443a0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_provider_skill',
    sa.Column('service_provider_id', sa.Integer(), nullable=True),
    sa.Column('service_skill_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['service_provider_id'], ['service_provider.id'], ),
    sa.ForeignKeyConstraint(['service_skill_id'], ['service_skill.id'], )
    )
    op.drop_constraint(u'service_skill_service_provider_id_fkey', 'service_skill', type_='foreignkey')
    op.drop_column(u'service_skill', 'service_provider_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'service_skill', sa.Column('service_provider_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'service_skill_service_provider_id_fkey', 'service_skill', 'service_provider', ['service_provider_id'], ['id'])
    op.drop_table('service_provider_skill')
    ### end Alembic commands ###
