# flake8: noqa
"""content

Revision ID: b07ea7c6869c
Revises: e7b02343dfac
Create Date: 2017-03-07 09:41:06.575590

"""

# revision identifiers, used by Alembic.
revision = 'b07ea7c6869c'
down_revision = 'e7b02343dfac'

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
        'content',
        PrimaryKey(),
        DefaultForeignKey('author', 'auth_user.id'),
        db.Column('uuid', db.String(32)),
        db.Column('type', db.String(32), nullable=False),
        db.Column('title', db.UnicodeText, nullable=True),
        db.Column('text', db.UnicodeText, nullable=True),
        db.Column('git', db.String(128), nullable=True),
        db.Column('creation_date', db.DateTime, nullable=True),
        db.Column('approval_date', db.DateTime, nullable=True),
        db.Column('published_date', db.DateTime, nullable=True),
        db.Column('self_destruct_date', db.DateTime, nullable=True),
        db.Column('json_metadata', db.Text, nullable=True),
        db.Column('private_key', db.Text, nullable=True),
        db.Column('public_key', db.Text, nullable=True),
    )
    op.create_table(
        'content_tag',
        PrimaryKey(),
        db.Column('uuid', db.String(32)),
        DefaultForeignKey('parent', 'content.id'),
        DefaultForeignKey('author', 'auth_user.id'),
        db.Column('text', db.Unicode(32), nullable=True),
    )
    op.create_table(
        'content_comment',
        PrimaryKey(),
        db.Column('uuid', db.String(32)),
        DefaultForeignKey('parent', 'content.id'),
        DefaultForeignKey('author', 'auth_user.id'),
        db.Column('text', db.UnicodeText),
        db.Column('creation_date', db.DateTime, nullable=True),
        db.Column('approval_date', db.DateTime, nullable=True),
        db.Column('published_date', db.DateTime, nullable=True),
    )
    op.create_table(
        'collaboration',
        PrimaryKey(),
        db.Column('uuid', db.String(32)),
        DefaultForeignKey('content', 'content.id'),
        DefaultForeignKey('peer', 'auth_user.id'),
        db.Column('type', db.String(32), nullable=False),
        db.Column('start_date', db.DateTime, nullable=True),
        db.Column('end_date', db.DateTime, nullable=True),
        db.Column('git', db.String(128), nullable=True),
        db.Column('json_metadata', db.Text, nullable=True),
        db.Column('private_key', db.Text, nullable=True),
        db.Column('public_key', db.Text, nullable=True),
    )



def downgrade():
    op.drop_table('collaboration')
    op.drop_table('content_tag')
    op.drop_table('content_text')
