"""Increase password field length

Revision ID: 9472aa966503
Revises: 4f29ff62b512
Create Date: 2024-07-25 23:54:00.081752

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9472aa966503'
down_revision = '4f29ff62b512'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)

    # ### end Alembic commands ###
