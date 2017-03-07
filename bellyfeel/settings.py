# -*- coding: utf-8 -*-
import os
import sys
from datetime import timedelta
from plant import Node

node = Node(__file__).dir
self = sys.modules[__name__]


self.MINIMUM_PASSWORD_LENGTH = 12
# sudo echo "127.0.0.1 bellyfeel.local" >> /etc/hosts
self.DOMAIN = os.environ.get('DOMAIN') or 'bellyfeel.local'
self.BASE_URL = os.environ.get('BASE_URL') or 'http://{}'.format(self.DOMAIN)
self.PRIVATE_PATH = os.environ.get('PRIVATE_PATH') or '/mnt/private'
self.MAIL_PATH = os.environ.get('MAIL_PATH') or '/srv/mail'
self.MAIL_DOMAINS = [
    'bellyfeel.io',
    'mail.bellyfeel.io',
]

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'mysql+mysqldb://root@localhost/bellyfeeldb')
SQLALCHEMY_TRACK_MODIFICATIONS = False

self.SECRET_KEY = os.environ.get('SECRET_KEY') or 'local'
self.SESSION_TYPE = 'memcached'

self.PERMANENT_SESSION_LIFETIME = timedelta(hours=6)
self.SESSION_KEY_PREFIX = 'bellyfeel:session:'
self.REDIS_CACHE_URI = os.environ.get('REDIS_CACHE_URI', 'redis://localhost:6379/0')
self.SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN', self.DOMAIN)
self.DEBUG = self.SECRET_KEY == 'local'
self.SESSION_COOKIE_SECURE = not self.DEBUG
self.FORCE_TOTP_TOKEN_ON_FIRST_LOGIN = False


def update(**kw):
    for key, value in kw.items():
        setattr(self, key, value)

    reload(self)
