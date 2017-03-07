# -*- coding: utf-8 -*-

from collections import OrderedDict
from flask_sqlalchemy import _BoundDeclarativeMeta


class ORM(object):
    def __init__(self):
        self.__registry__ = OrderedDict()

    def register(self, name, Model):
        self.__registry__[name] = Model
        assert self.__registry__[name] == Model
        return Model

    def __getattr__(self, attr_name):
        if attr_name.startswith('__'):
            return super(ORM, self).__getattribute__(attr_name)

        return self.__registry__.get(attr_name)

    def to_dict(self):
        return self.__registry__.copy()


orm = ORM()


class MetaModel(_BoundDeclarativeMeta):

    def __init__(cls, name, bases, attrs):
        orm.register(name, cls)
        super(MetaModel, cls).__init__(name, bases, attrs)
