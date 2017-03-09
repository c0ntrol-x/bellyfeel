#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import io
import os
import functools
import hashlib
from datetime import datetime
from flask import request
from flask import Response

from flask import g
from flask import session
from flask import url_for
from flask import redirect
from p4rr0t007.lib.core import slugify

from bellyfeel.sql import db
from bellyfeel.sql import SQLSession
from bellyfeel.sql import Content
from bellyfeel.sql import User
from bellyfeel import settings

from bellyfeel.http import server
from bellyfeel.http import logger
from bellyfeel.http import node


def log_and_respond_bad_request(template_name, error_message):
    logger.warning(error_message)
    errors = [error_message]
    return server.template_response(template_name, dict(errors=errors), code=400)


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
        if g.user and g.user.is_admin:
            context = dict(user=g.user)
            if settings.FORCE_TOTP_TOKEN_ON_FIRST_LOGIN and g.user.must_reset_password():
                context['errors'] = [
                    'your password must be reset before proceeding'
                ]
                return server.template_response('admin/change_password.html', context)

            if settings.FORCE_TOTP_TOKEN_ON_FIRST_LOGIN and g.user.must_set_totp_token():
                context['errors'] = [
                    'your must set a TOTP token before proceeding'
                ]
                return server.template_response('admin/reset_totp_token.html', context)

            return func(*args, **kw)
        else:
            logger.warning('unauthorized access {}'.format(repr(dict(request.headers))))
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


def get_template_safe_settings_as_dict():
    safe_settings = [
        'MINIMUM_PASSWORD_LENGTH',
        'DEBUG',
        'DOMAIN',
        'BASE_URL',
    ]

    return dict([(name, getattr(settings, name)) for name in safe_settings])


@server.context_processor
def inject_user_and_settings():
    return dict(
        user=g.user,
        settings=get_template_safe_settings_as_dict()
    )


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

    session['admin_uuid'] = user.uuid
    g.user = user
    logger.info('server welcomes a new session from user {}'.format(email))
    return redirect(url_for('admin_dashboard'))


# --------------------------------------------------------------


@server.route("/out")
def admin_logout():
    user = getattr(g, 'user', None)
    if user:
        logger.critical('server says good bye to user: {}'.format(user.email))
        session.clear()

    return redirect(url_for('index'))


@server.route("/0nion")
def onion():
    return server.template_response('onion.html')


@server.route("/content/<int:id>/markdown")
@admin_only
def admin_edit_content(id):
    if g.user.profile.get('prefer_markdown_editor'):
        return server.json_response({'url': url_for('edit_content_markdown', id=id)})
    else:
        return server.json_response({'url': url_for('edit_content_quill', id=id)})


@server.route("/content/<int:id>/delete", methods=['GET', 'POST', 'DELETE'])
@admin_only
def admin_delete_content(id):
    content = Content.query_by(id=id).first()
    if not content:
        return redirect(url_for('admin_draft_list'))

    if request.method.upper() in ('POST', 'DELETE'):
        content.delete()
        return redirect(url_for('admin_draft_list'))

    return server.template_response('admin/content.delete.html', dict(user=g.user, content=content))


@server.route("/content/<int:id>/edit")
@admin_only
def admin_edit_content_preferred(id):
    if g.user.profile.get('prefer_markdown_editor'):
        return redirect(url_for('edit_content_markdown', id=id))
    else:
        return redirect(url_for('edit_content_quill', id=id))


@server.route("/content/<int:id>/markdown")
@admin_only
def edit_content_markdown(id):
    content = Content.query_by(id=id).first()
    if not content:
        return redirect(url_for('admin_draft_list'))

    return server.template_response('admin/editor.markdown.html', dict(user=g.user, content=content))


@server.route("/content/markdown")
@admin_only
def create_content_markdown():
    return server.template_response('admin/editor.markdown.html', dict(user=g.user, content=None))


@server.route("/content/<int:id>/wysiwyg")
@admin_only
def edit_content_quill(id):
    content = Content.query_by(id=id).first()
    if not content:
        return redirect(url_for('admin_draft_list'))

    return server.template_response('admin/editor.quill.html', dict(user=g.user, content=content))


@server.route("/content/wysiwyg")
@admin_only
def create_content_quill():
    return server.template_response('admin/editor.quill.html', dict(user=g.user, content=None))


@server.route("/api/content/save", methods=['POST'])
@admin_only
def api_content_create():
    data = server.get_json_request()
    title = data.get('title', '').strip() or 'Untitled {}'.format(datetime.utcnow().isoformat())
    markdown_text = data.get('markdown_text', '')
    quill_text = data.get('quill_text', '')
    text = markdown_text or quill_text
    type = data.get('type', 'note').lower()

    item = Content.create(
        author=g.user.id,
        title=slugify(title),
        type=type,
        text=text,
        creation_date=datetime.utcnow(),
    )
    return server.json_response({
        'url': item.url
    })


@server.route("/api/content/<int:id>/save", methods=['POST', 'DELETE'])
@admin_only
def api_content_edit(id):
    item = Content.query_by(id=id).first()

    if request.method.upper() == 'DELETE':
        item.delete()
        return server.json_response({
            'url': url_for('admin_dashboard')
        })

    data = server.get_json_request()
    title = data.get('title', '').strip()
    markdown_text = data.get('markdown_text', '')
    quill_text = data.get('quill_text', '')
    text = markdown_text or quill_text
    type = data.get('type', 'note').lower()
    self_destruct_date = data.get('self_destruct_date', 'note').lower()

    if title:
        item.title = title

    if text:
        item.text = text

    if type:
        item.type = type

    if self_destruct_date:
        item.self_destruct_date = self_destruct_date

    item.save()

    return server.json_response({
        'url': item.url
    })


@server.route("/outliner")
@admin_only
def admin_outliner():
    return server.template_response('admin/outliner.html', dict(user=g.user))


@server.route("/drafts")
@admin_only
def admin_draft_list():
    content_list = g.user.get_drafts()
    return server.template_response('admin/content.list.html', dict(user=g.user, content_list=content_list))


@server.route("/tags")
@admin_only
def admin_tag_list():
    content_list = g.user.get_tags()
    return server.template_response('admin/content.list.html', dict(user=g.user, content_list=content_list))


@server.route("/comments")
@admin_only
def admin_comment_list():
    content_list = g.user.get_comments()
    return server.template_response('admin/content.list.html', dict(user=g.user, content_list=content_list))


@server.route("/collaborations")
@admin_only
def admin_collaboration_list():
    content_list = g.user.get_collaborations()
    return server.template_response('admin/content.list.html', dict(user=g.user, content_list=content_list))


@server.route("/notes")
@admin_only
def admin_note_list():
    content_list = g.user.get_notes()
    return server.template_response('admin/content.list.html', dict(user=g.user, content_list=content_list))


@server.route("/reminders")
@admin_only
def admin_reminder_list():
    content_list = g.user.get_reminders()
    return server.template_response('admin/content.list.html', dict(user=g.user, content_list=content_list))


@server.route("/tasks")
@admin_only
def admin_task_list():
    content_list = g.user.get_tasks()
    return server.template_response('admin/content.list.html', dict(user=g.user, content_list=content_list))


@server.route("/published")
@admin_only
def admin_published_list():
    content_list = g.user.get_published()
    return server.template_response('admin/content.list.html', dict(user=g.user, content_list=content_list))


@server.route("/expired")
@admin_only
def admin_expired_list():
    content_list = g.user.get_expired()
    return server.template_response('admin/content.list.html', dict(user=g.user, content_list=content_list))


@server.route("/account/password")
@admin_only
def admin_change_password():
    return server.template_response('admin/change_password.html', dict(user=g.user))


@server.route("/profile")
@admin_only
def admin_profile():
    return server.template_response('admin/profile.html', dict(user=g.user))


@server.route("/mail")
@admin_only
def admin_mail():
    return server.template_response('admin/mail.html', dict(user=g.user))


@server.route("/a/dash")
@admin_only
def admin_dashboard():
    return server.template_response('admin/index.html', dict(user=g.user))


@server.route("/s/totp.png")
@admin_only
def admin_render_temporary_totp_token():
    pngbytes = io.BytesIO()
    g.user.write_qrcode_to_buffer(pngbytes)
    pngbytes.seek(0)
    return Response(pngbytes, headers={'Content-Type': 'application/octet-stream'})


@server.route("/account/password/change", methods=['POST'])
def admin_change_password_post():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    repeat_new_password = request.form['repeat_new_password']
    template_name = 'admin/change_password.html'

    if len(new_password) < settings.MINIMUM_PASSWORD_LENGTH:
        return log_and_respond_bad_request(
            template_name,
            'password must have at least 12 characters',
        )

    if not g.user.match_password(current_password):
        return log_and_respond_bad_request(
            template_name,
            'invalid password',
        )

    if new_password != repeat_new_password:
        return log_and_respond_bad_request(
            template_name,
            'invalid password',
        )

    if not g.user.change_password(new_password):
        return log_and_respond_bad_request(
            template_name,
            'failed to change password',
        )

    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':

    settings.update(
        SECRET_KEY=os.urandom(32).encode('base64').strip(),
        MAIL_PATH=node.dir.parent.join('mail'),
    )
    server.run(debug=True, port=1984, host='oldspeak')
