"""empty message

Revision ID: 298bbf22bdb8
Revises: b976e7a7dc35
Create Date: 2017-04-02 13:11:00.655727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '298bbf22bdb8'
down_revision = 'b976e7a7dc35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('person', sa.Column('is_admin', sa.Boolean()))
    op.add_column('person', sa.Column('is_brewer', sa.Boolean()))
    op.add_column('person', sa.Column('is_manager', sa.Boolean()))
    op.execute('UPDATE person SET is_admin=False, is_brewer=False, is_manager=False')
    op.alter_column('person', 'is_admin', nullable=False)
    op.alter_column('person', 'is_brewer', nullable=False)
    op.alter_column('person', 'is_manager', nullable=False)

    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('person', 'is_manager')
    op.drop_column('person', 'is_brewer')
    op.drop_column('person', 'is_admin')
    # ### end Alembic commands ###