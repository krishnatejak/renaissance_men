"""Update job status_type enum

Revision ID: cff1d3443a0
Revises: 4bd773af3481
Create Date: 2015-02-07 11:28:20.630981

"""

# revision identifiers, used by Alembic.
revision = 'cff1d3443a0'
down_revision = '4bd773af3481'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


old_options = ('assigned', 'quoted', 'started', 'complete')
new_options = ('assigned', 'accepted', 'rejected', 'started', 'complete')

old_type = sa.Enum(*old_options, name='status_types')
new_type = sa.Enum(*new_options, name='status_types')
tmp_type = sa.Enum(*new_options, name='_status_types')

def upgrade():
    # Create a tempoary "_status" type, convert and drop the "old" type                                                                                                            
    tmp_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE job ALTER COLUMN status TYPE _status_types'
               ' USING status::text::_status_types');
    old_type.drop(op.get_bind(), checkfirst=False)
    # Create and convert to the "new" status type                                                                                                                                  
    new_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE job ALTER COLUMN status TYPE status_types'
               ' USING status::text::status_types');
    tmp_type.drop(op.get_bind(), checkfirst=False)


def downgrade():
    pass
