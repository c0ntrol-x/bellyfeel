#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import json
import logging
import functools
import hashlib
from flask import request
import coloredlogs

from flask import g
from flask import session
from flask import url_for
from flask import redirect
from p4rr0t007.lib.core import slugify

from bellyfeel.sql import db
from bellyfeel.sql import SQLSession
from bellyfeel.sql import User
from bellyfeel import settings

from bellyfeel.http import server
from bellyfeel.http import logger
from bellyfeel.http import node


@server.route("/")
def index():
    if not g.user:
        return redirect(url_for('admin_login'))
    elif g.user.is_admin:
        return redirect(url_for('admin_dashboard'))

    return server.template_response('index.html', dict(user=g.user))


@server.route("/.check")
def online_check():
    return server.text_response('OK')


@server.route("/api/login", methods=['POST'])
def api_login_post():
    api_token = hashlib.sha512(repr(request.headers)).hexdigest()

    return server.json_response({
        'api_token': api_token
    })


# auth
# --------------------------------------------------------------
def admin_only(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        import ipdb;ipdb.set_trace()
        if g.user and g.user.is_admin:
            return func(*args, **kw)
        else:
            logger.info('unauthorized access')
            return server.template_response('forbidden.html', code=403)

    return wrapper


@server.before_request
def retrieve_session_user():
    uid_key = 'admin_uuid'

    if uid_key not in session:
        g.user = None
        return

    uid = session[uid_key]
    g.user = SQLSession(db.session).query_first_by(User, uuid=uid)


@server.route("/in")
def admin_login():
    return server.template_response('login.html')


@server.route("/in", methods=['POST'])
def admin_login_post():
    email = request.form['email']
    password = request.form['password']

    user = User.authenticate(email, password)
    if not user:
        logger.warning('failed to authenticate user {}'.format(email))
        return server.template_response('login.html', dict(errors=['invalid credentials']))

    server.session['admin_uuid'] = user.uuid
    g.user = user
    logger.critical('server welcomes a new session from user {}'.format(email))
    # import ipdb;ipdb.set_trace()
    return server.template_response('admin/index.html', dict(user=g.user))


# --------------------------------------------------------------


@server.route("/out")
def admin_logout():
    user = getattr(g, 'user', None)
    if user:
        logger.critical('server says good bye to user: {}'.format(user.email))
        server.session.clear()

    return redirect(url_for('index'))


@server.route("/0nion")
def onion():
    return server.template_response('onion.html')


@server.route("/e/<path:path>", methods=['GET'])
def editor(path):
    name = path.split('/')[-1]
    post = {
        'slug': slugify(path),
        'path': path,
        'name': name,
    }
    post['id'] = hashlib.sha512(json.dumps(post)).hexdigest()
    return server.template_response('editor.new.html', dict(user=g.user, post=post, json_post=json.dumps(post)))


@server.route("/e/save/<path:path>", methods=['POST'])
def editor_save(path):
    return server.template_response('editor.draft.html', dict(user=g.user))


@server.route("/a/dash")
@admin_only
def admin_dashboard():
    return server.template_response('admin/index.html', dict(user=g.user))


if __name__ == '__main__':
    coloredlogs.install(level=logging.DEBUG)
    settings.update(
        SECRET_KEY=os.urandom(32).encode('base64').strip(),
        MAIL_PATH=node.dir.parent.join('mail'),
    )
    server.run(debug=True)
