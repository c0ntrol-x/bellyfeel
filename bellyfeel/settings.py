# -*- coding: utf-8 -*-
import os
import sys
from datetime import timedelta
from plant import Node

node = Node(__file__).dir
self = sys.modules[__name__]


self.BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5000'
self.PRIVATE_PATH = os.environ.get('PRIVATE_PATH') or '/mnt/private'
self.MAIL_PATH = os.environ.get('MAIL_PATH') or '/srv/mail'
self.MAIL_DOMAINS = [
    'bellyfeel.io',
    'mail.bellyfeel.io',
]

SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@localhost/bellyfeeldb'
SQLALCHEMY_TRACK_MODIFICATIONS = False

self.SECRET_KEY = os.environ.get('SECRET_KEY') or 'local'
self.SESSION_TYPE = 'memcached'
self.SESSION_COOKIE_SECURE = True
self.PERMANENT_SESSION_LIFETIME = timedelta(hours=6)
self.SESSION_KEY_PREFIX = 'bellyfeel:session:'
self.REDIS_CACHE_URI = 'redis://localhost:6379/0'

self.DEBUG = False


def update(**kw):
    for key, value in kw.items():
        setattr(self, key, value)

    if self.DEBUG:
        sys.stderr.write('\033[1;33m\n<settings>\n{}\n</settings>\n\033[0m'.format("\n".join(["{}={}".format(k, v) for k, v in self.__dict__.items() if k.upper() == k])))
