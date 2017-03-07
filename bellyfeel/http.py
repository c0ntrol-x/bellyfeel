#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from plant import Node
from p4rr0t007.web import Application
from p4rr0t007.lib.core import get_logger


node = Node(__file__)
server = Application(node, settings_module='bellyfeel.settings')
logger = get_logger()


__all__ = [
    'server',
    'logger',
    'node',
]
