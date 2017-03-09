# -*- coding: utf-8 -*-
import json
from bellyfeel.sql import User
from tests.functional.scenarios import session_url


@session_url('/in')
def test_admin_login_ok(context):
    ('POST /in with email + password should login an admin user')

    # Given an API Client with a pre-existing active user
    email = 'foo@bar.com'
    password = '1n5EcUr3@$phuck'

    # And that a user exists
    User.create_with_password(email, password).activate_now(is_admin=True)

    # When I request a login
    response = context.http.post(
        '/in',
        data=json.dumps({
            'email': email,
            'password': password,
            'repeat_new_password': password,
        }),
        headers={
            'Content-Type': 'application/json'
        },
        follow_redirects=True,
    )

    # Then it should have returned 302
    response.status_code.should.equal(302)

    # And it should have redirected
    response.headers.should.have.key('Location').being.equal('http://localhost/a/dash')
