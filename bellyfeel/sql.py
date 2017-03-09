# -*- coding: utf-8 -*-
import os
import io
import sys
import json
import pyotp
import qrcode
import random
import bcrypt
from uuid import uuid4
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.ext.declarative import declared_attr

from bellyfeel import settings
from bellyfeel import networking
from bellyfeel.meta import MetaModel
from bellyfeel.http import server
from p4rr0t007.lib.core import get_logger


db = SQLAlchemy(server)
server.models = sys.modules[__name__]

logger = get_logger('bellyfeel.db')


def generate_password(length=12):
    return os.urandom(length * 2).encode('base64').strip().strip('=').encode('rot13')[:7]


def DefaultForeignKey(field_name, parent_field_name,
                      ondelete='CASCADE', nullable=False, **kw):
    return db.Column(field_name, db.Integer,
                     db.ForeignKey(parent_field_name, ondelete=ondelete),
                     nullable=nullable, **kw)


def PrimaryKey(name='id'):
    return db.Column(name, db.Integer, primary_key=True)


def get_redis_pool():
    return networking.cache.get_redis_pool(settings.REDIS_CACHE_URI)


def get_redis_connection():
    return networking.cache.get_redis_connection(get_redis_pool())


class SQLSession(object):
    def __init__(self, session=None):
        self.session = session or db.sessionmaker(autocommit=True)

    def modify(self, *dirty_objects):
        cycles = []
        for model in dirty_objects:
            if isinstance(model, (list, tuple)):
                cycles.extend(map(self.session.add, model))
            elif isinstance(model, db.Model):
                cycles.append(self.session.add(model))

        ok = self.session.commit()
        self.session.flush()
        return ok, cycles

    def create(self, *dirty_objects):
        return self.modify(*dirty_objects)

    def query_by(self, ModelClass, **kw):
        q = self.session.query(ModelClass)
        for field, value in kw.items():
            if isinstance(value, BellyfeelModel):
                value = value.id

            operation = None
            if '__' in field:
                field, operation = field.split('__', 1)

            column = getattr(ModelClass.__table__.c, field)
            if operation == 'not':
                q = q.filter(column != value)
            elif operation == 'gt':
                q = q.filter(column > value)
            elif operation == 'gte':
                q = q.filter(column >= value)
            elif operation == 'lt':
                q = q.filter(column < value)
            elif operation == 'lte':
                q = q.filter(column <= value)
            else:
                q = q.filter(column == value)

        return q

    def query_first_by(self, ModelClass, **kw):
        return self.query_by(ModelClass, **kw).first()

    def get_all_by(self, ModelClass, **kw):
        return self.session.query(ModelClass).filter(**kw).all()


class UserMetadata(OrderedDict):
    fields = (
        ('force_password_change', bool)
    )

    @classmethod
    def create(cls, **kw):
        data = {}
        for k, v in kw.items():
            cast = cls.fields.get(k, bytes)
            data[k] = cast(v)

        return cls

    def to_json(self, **kw):
        return json.dumps(self, **kw)


class BellyfeelModel(db.Model):
    __abstract__ = True

    __table_args__ = {
        'mysql_engine': 'InnoDB'
    }
    __mapper_args__ = {
        'always_refresh': True
    }
    __metaclass__ = MetaModel

    def __init__(self, **kw):
        self.id = None
        for k, v in kw.items():
            setattr(self, k, v)

        self.initialize()

    def initialize(self):
        pass

    def __repr__(self):
        return '<{0}({1})>'.format(self.__class__.__name__, self.id and 'id={}'.format(self.id) or '')

    def save(self):
        session = SQLSession(db.session)
        ok, cycles = session.modify(self)
        return self

    def delete(self):
        db.session.execute(self.__table__.delete(self.__table__.c.id == self.id))
        return db.session.commit()

    @classmethod
    def all(cls):
        return cls.query_by()

    @classmethod
    def query_by(cls, **kw):
        return SQLSession(db.session).query_by(cls, **kw)

    @classmethod
    def create(cls, **kw):
        """Creates a model instance with arbitrary keyword-args that must map to
        existing field names and valid values.  This method does not
        perform application-level validation, but might raise original
        SQLAlchemy exceptions in case a field does meet a SQL-level
        validation.

        Auto-commits the transaction.

        :param **kw: key-word args are mapped to valid model fields.
        :returns: an instance of the model, stored in mysql
        :raises: original SQLAlchemy exceptions
        """
        model_instance = cls(**kw)
        db.session.add(model_instance)
        db.session.commit()
        return model_instance


class ActionTreeNodeController(object):
    known_parents = ()

    def __init__(self, parent, validate_parent=True, *args, **kw):
        self.__parent_node__ = parent
        self.should_validate_parent = validate_parent

        self.initialize(*args, **kw)

    def initialize(self, *args, **kw):
        pass

    def set_parent(self, parent):
        self.__parent_node__ = parent
        return parent

    def parent_is_valid(self, parent):
        if not self.should_validate_parent:
            return True

        return isinstance(parent, (db.Model, self.known_parents))

    def get_parent(self):
        parent = self.__parent_node__
        if not self.parent_is_valid(parent):
            raise InvalidActionHelperParent(self, parent)

        return parent

    parent = property(fset=set_parent, fget=get_parent)


class ModelActionController(ActionTreeNodeController):
    known_parents = (ActionTreeNodeController, )


class ActionHelper(ActionTreeNodeController):
    known_parents = (ActionTreeNodeController, )
    """subclass of :py:cls:`ActionTreeNodeController` that only handles other ActionTreeNodeController instances"""
    def parent_is_valid(self, parent):
        return isinstance(parent, db.Model)


class APIUserRedisTokenHelper(ActionHelper):
    def for_api_token(self, token):
        return 'bellyfeel:api:tokens:user:{token}'.format(**locals())


class RedisModelHelper(ActionHelper):
    @property
    def pool(self):
        return get_redis_pool()

    @property
    def connection(self):
        return get_redis_connection()


class UserAPIActionController(ModelActionController):
    def initialize(self):
        self.redis = RedisModelHelper(self)
        self.redis_key = APIUserRedisTokenHelper(self)

    def get_token_ttl(self, token):
        key = self.redis_key.for_api_token(token)
        return self.redis.connection.ttl(key)


class User(BellyfeelModel):
    __tablename__ = 'auth_user'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), default=lambda: uuid4().hex)
    email = db.Column(db.String(92))
    password = db.Column(db.String(128))
    activation_date = db.Column(db.DateTime, nullable=True)
    json_metadata = db.Column(db.Text, nullable=True)
    totp_token = db.Column(db.String(16), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    last_access_date = db.Column(db.DateTime, nullable=True)
    password_change_date = db.Column(db.DateTime, nullable=True)
    first_name = db.Column(db.String(27))
    last_name = db.Column(db.String(27))
    photo_url = db.Column(db.UnicodeText)

    def has_notifications(self):
        return True

    def must_reset_password(self):
        if self.password_change_date is None:
            return True

        max_expiration_date = self.password_change_date + timedelta(days=60)
        return self.password_change_date >= max_expiration_date

    def must_set_totp_token(self):
        return self.totp_token is None

    def get_notifications(self):
        return [
            {
                'href': '#',
                'message': 'Revision Feedback',
                'badge': '2',
                'level': 'success',
            },
            {
                'href': '#',
                'message': 'forum replies',
                'badge': '27',
            },
        ]

    def has_unread_messages(self):
        return True

    def get_unread_messages(self):
        usernames = [
            'd4v1ncy',
            '0rbitaeolian',
            'th0ughtcr1me',
        ]
        notme = sorted(set(usernames).difference({self.username}))

        return [
            {
                'href': '#',
                'when': '2 weeks ago',
                'preview': 'Enjoy the UI mockups...',
                'sender': random.choice(usernames),
                'sender_image_path': url_for('static', filename='img/{}.jpeg'.format(random.choice(notme))),
            },
            {
                'href': '#',
                'preview': 'Hola ...',
                'when': 'Yesterday at 4:20 PM',
                'sender': random.choice(usernames),
                'sender_image_path': url_for('static', filename='img/{}.jpeg'.format(random.choice(notme))),
            },
            {
                'href': '#',
                'sender': random.choice(usernames),
                'preview': 'Oh, one more thing ...',
                'when': 'about 27 minutes ago',
                'sender_image_path': url_for('static', filename='img/{}.jpeg'.format(random.choice(notme))),
            },
        ]

    def initialize(self):
        self.api = UserAPIActionController(self)

    def get_published(self):
        return Content.query_by(author=self, self_destruct_date__lte=datetime.utcnow())

    def total_published(self):
        return self.get_published().count()

    def get_expired(self):
        return Content.query_by(author=self, self_destruct_date__lte=datetime.utcnow())

    def total_expired(self):
        return self.get_expired().count()

    def get_drafts(self):
        return Content.query_by(author=self, published_date=None)

    def total_drafts(self):
        return self.get_drafts().count()

    def get_notes(self):
        return Content.query_by(author=self, type='note')

    def total_notes(self):
        return self.get_notes().count()

    def get_tasks(self):
        return Content.query_by(author=self, type='task')

    def total_tasks(self):
        return self.get_tasks().count()

    def get_reminders(self):
        return Content.query_by(author=self, type='auto-reminder')

    def total_reminders(self):
        return self.get_reminders().count()

    def get_comments(self):
        return Comment.query_by(author=self)

    def total_comments(self):
        return self.get_comments().count()

    def get_collaborations(self):
        return Collaboration.query_by(peer=self)

    def total_collaborations(self):
        return self.get_collaborations().count()

    def get_tags(self):
        return Tag.query_by(author=self)

    def total_tags(self):
        return self.get_tags().count()

    @property
    def profile(self):
        try:
            return json.loads(self.json_metadata)
        except (TypeError, ValueError):
            return {}

    @property
    def username(self):
        return self.email.split('@', 1)[0]

    @property
    def totp(self):
        return pyotp.TOTP(self.totp_token)

    @property
    def totp_provisioning_uri(self):
        return self.totp.provisioning_uri(self.email)

    def activate_now(self, is_admin=False):
        if self.activation_date is not None:
            raise UserAlreadyActivated(self)

        new_token = pyotp.random_base32()
        self.is_admin = bool(is_admin)
        self.activation_date = datetime.utcnow()
        self.totp_token = new_token
        return self.save()

    def write_qrcode_to_buffer(self, filelike):
        img = qrcode.make(self.totp_provisioning_uri)
        return img.save(filelike)

    def change_password(self, newpw):
        self.password = self.secretify_password(newpw)
        self.password_change_date = datetime.utcnow()
        return self.save()

    def reset_password(self):
        newpw = generate_password(17)
        if self.change_password(newpw):
            return newpw

    def get_qrcode_png_bytes(self):
        out = io.BytesIO()
        self.write_qrcode_to_buffer(out)
        return out.getvalue()

    def validate_code(self, code):
        return bytes(code) == bytes(self.totp.now())

    def reset_totp_token(self, force=False):
        if self.totp_token is not None and force is False:
            raise UserTOTPTokenResetConfirmationRequired(user=self)
        new_token = pyotp.random_base32()
        logger.info('resetting totp token of user {}'.format(self))
        return self.save(totp_token=new_token).totp_token

    def match_password(self, plain):
        return self.password == bcrypt.hashpw(plain, self.password)

    def set_admin(self, admin=True):
        self.is_admin = admin
        if admin:
            logger.info('adding admin clearance to user {}'.format(self))
        else:
            logger.info('removing admin clearance to user {}'.format(self))

        self.save()

    @classmethod
    def authenticate(cls, email, password):
        logger.info('attempting to authenticate email {}'.format(email))
        email = email.lower()
        user = SQLSession(db.session).query_first_by(cls, email=email)
        if not user:
            logger.info('email does not exist {}'.format(email))
            return

        if user.match_password(password):
            logger.info('authenticated user {}'.format(user))
            return user

        logger.warning('failed to authenticate user {}'.format(user))

    @classmethod
    def secretify_password(cls, plain):
        return bcrypt.hashpw(plain, bcrypt.gensalt(12))

    @classmethod
    def create(cls, email, password, **kw):

        email = email.lower()
        password = cls.secretify_password(password)
        if not kw.get('json_metadata'):
            kw['json_metadata'] = json.dumps({
                'prefer_markdown_editor': False,
            })

        return super(User, cls).create(email=email, password=password, **kw)

    @classmethod
    def create_with_password(cls, email, password):
        user = cls.get_by_email(email)
        if user:
            raise UserAlreadyExists(email)

        return cls.create(email=email, password=password)

    @classmethod
    def get_by_email(cls, email):
        # import ipdb;ipdb.set_trace()
        user = db.session.query(User).filter_by(email=email).first()
        return user


class Content(BellyfeelModel):
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), default=lambda: uuid4().hex)
    author = DefaultForeignKey('author', 'auth_user.id')
    type = db.Column(db.String(32), nullable=False)
    title = db.Column(db.UnicodeText, nullable=True)
    text = db.Column(db.UnicodeText, nullable=True)
    git = db.Column(db.String(128), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=True)
    approval_date = db.Column(db.DateTime, nullable=True)
    published_date = db.Column(db.DateTime, nullable=True)
    self_destruct_date = db.Column(db.DateTime, nullable=True)
    json_metadata = db.Column(db.Text, nullable=True)
    private_key = db.Column(db.Text, nullable=True)
    public_key = db.Column(db.Text, nullable=True)

    @property
    def url(self):
        return url_for('admin_edit_content_preferred', id=self.id)


class Tag(BellyfeelModel):
    __tablename__ = 'content_tag'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), default=lambda: uuid4().hex)
    parent = DefaultForeignKey('parent', 'content.id')
    author = DefaultForeignKey('author', 'auth_user.id')
    text = db.Column(db.UnicodeText, nullable=True)


class Comment(BellyfeelModel):
    __tablename__ = 'content_comment'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), default=lambda: uuid4().hex)
    parent = DefaultForeignKey('parent', 'content.id')
    author = DefaultForeignKey('author', 'auth_user.id')
    text = db.Column(db.UnicodeText, nullable=True)
    creation_date = db.Column(db.DateTime, nullable=True)
    approval_date = db.Column(db.DateTime, nullable=True)
    published_date = db.Column(db.DateTime, nullable=True)


class Collaboration(BellyfeelModel):
    __tablename__ = 'collaboration'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), default=lambda: uuid4().hex)
    content = DefaultForeignKey('content', 'content.id')
    author = DefaultForeignKey('peer', 'auth_user.id')
    type = db.Column(db.String(32), nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    git = db.Column(db.String(128), nullable=True)
    json_metadata = db.Column(db.Text, nullable=True)
    private_key = db.Column(db.Text, nullable=True)
    public_key = db.Column(db.Text, nullable=True)


class BellyfeelException(Exception):
    """base exception"""


class UserAlreadyExists(BellyfeelException):
    pass


class EmailCallbackException(BellyfeelException):
    """sub-classes of this exception automatically send an email to the
    user with a confirmation link that, after validated and confirmed by
    the user, will trigger a "resume" action in one of the background
    workers."""

    def __init__(self, user):
        self.user = user


class UserTOTPTokenResetConfirmationRequired(EmailCallbackException):
    pass


class InvalidActionHelperParent(BellyfeelException):
    pass


class UserAlreadyActivated(BellyfeelException):
    pass
