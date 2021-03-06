"""empty message

Revision ID: 34223fdff008
Revises: b4bcea5528b6
Create Date: 2017-08-22 10:19:27.959749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34223fdff008'
down_revision = 'b4bcea5528b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('person', sa.Column('default_brewery', sa.Integer(), nullable=True))
    op.add_column('person', sa.Column('default_location', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('person', 'default_location')
    op.drop_column('person', 'default_brewery')
    # ### end Alembic commands ###
