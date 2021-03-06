"""empty message

Revision ID: 3e421d588b08
Revises: 
Create Date: 2017-03-30 01:02:04.225125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e421d588b08'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tap',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tap')
    # ### end Alembic commands ###
