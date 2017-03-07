# flake8: noqa
"""initial user model

Revision ID: adbc37419223
Revises: None
Create Date: 2017-03-03 18:34:19.727017

"""

# revision identifiers, used by Alembic.
revision = 'adbc37419223'
down_revision = None

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
    op.create_table(
        'auth_user',
        db.Column('id', db.Integer, primary_key=True),
        db.Column('uuid', db.String(32)),
        db.Column('email', db.String(256), unique=True),
        db.Column('password', db.String(128)),
        db.Column('activation_date', db.DateTime, nullable=True),
        db.Column('json_metadata', db.Text, nullable=True),
        db.Column('totp_token', db.String(16), nullable=True),
        db.Column('is_admin', db.Boolean, default=False),
        db.Column('last_access_date', db.DateTime, nullable=True),
        db.Column('password_change_date', db.DateTime, nullable=True),
    )



def downgrade():
    op.drop_table('auth_user')
