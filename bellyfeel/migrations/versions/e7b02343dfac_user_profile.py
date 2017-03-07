# flake8: noqa
"""user-profile


Revision ID: e7b02343dfac
Revises: adbc37419223
Create Date: 2017-03-07 08:45:27.475797

"""

# revision identifiers, used by Alembic.
revision = 'e7b02343dfac'
down_revision = 'adbc37419223'

from datetime import datetime
from alembic import op
import sqlalchemy as db




def DefaultForeignKey(field_name, parent_field_name,
                      ondelete='CASCADE', nullable=False, **kw):
    return db.Column(field_name, db.Integer,
                     db.ForeignKey(parent_field_name, ondelete=ondelete),
                     nullable=nullable, **kw)


def PrimaryKey(name='id'):
    return db.Column(name, db.Integer, primary_key=True)


def now():
    return datetime.now()


def upgrade():
    op.alter_column(
        'auth_user', 'email',
        existing_type=db.String(256),
        type_=db.String(92),
    )
    op.create_unique_constraint("uq_email", "auth_user", ["email"])

    op.add_column('auth_user', db.Column('first_name', db.Unicode(27), nullable=True))
    op.add_column('auth_user', db.Column('last_name', db.Unicode(27), nullable=True))
    op.add_column('auth_user', db.Column('photo_url', db.UnicodeText, nullable=True))
    op.add_column('auth_user', db.Column('private_key', db.Text, nullable=True))
    op.add_column('auth_user', db.Column('public_key', db.Text, nullable=True))


def downgrade():
    op.drop_constraint("uq_email", "auth_user", "unique")
    op.drop_column('auth_user', 'last_name')
    op.drop_column('auth_user', 'first_name')
    op.alter_column(
        'auth_user', 'email',
        existing_type=db.String(92),
        type_=db.String(256),
    )
