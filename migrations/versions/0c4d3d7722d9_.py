"""empty message

Revision ID: 0c4d3d7722d9
Revises: 602fa0cf66f9
Create Date: 2017-08-23 23:28:01.689046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c4d3d7722d9'
down_revision = '602fa0cf66f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('location', sa.Column('short_name', sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, 'location', ['short_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'location', type_='unique')
    op.drop_column('location', 'short_name')
    # ### end Alembic commands ###
