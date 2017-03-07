# -*- coding: utf-8 -*-
from repocket import ActiveRecord, attributes


class SessionData(ActiveRecord):
    email = attributes.Bytes()
    data = attributes.JSON()
