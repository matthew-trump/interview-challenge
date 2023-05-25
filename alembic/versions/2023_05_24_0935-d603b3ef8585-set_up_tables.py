"""Set up tables

Revision ID: d603b3ef8585
Revises: a6069f5ea253
Create Date: 2023-05-24 09:35:05.431128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd603b3ef8585'
down_revision = 'a6069f5ea253'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'business', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'business', type_='unique')
    # ### end Alembic commands ###