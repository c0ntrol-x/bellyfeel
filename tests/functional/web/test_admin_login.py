# -*- coding: utf-8 -*-

from bellyfeel.sql import User
from tests.functional.scenarios import api_test


@api_test
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
        data={
            'email': email,
            'password': password,
        },
        headers={
            'Content-Type': 'multipart/form-data'
        }
    )

    # Then it should have returned 302
    response.status_code.should.equal(302)

    # And it should have redirected
    response.headers.should.have.key('Location').being.equal('http://localhost/')

    response = context.http.get('/a/dash')

    response.status_code.should.equal(200)
