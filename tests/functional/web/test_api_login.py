# -*- coding: utf-8 -*-
import json
from tests.functional.helpers import APIClient
from tests.functional.scenarios import api_test


@api_test
def test_api_login_ok(context):
    ('/api/login should return a temporary redis token')

    # Given an API Client with a pre-existing active user
    api = APIClient(context.http)
    email = 'foo@bar.com'
    password = '1n5EcUr3@$phuck'

    # And that a user exists
    user = api.create_active_user(email, password)

    # When I request a login
    response = context.http.post(
        '/api/login',
        data=json.dumps({
            'email': email,
            'password': password,
        }),
        headers={
            'Content-Type': 'application/json'
        }
    )

    # Then it should have returned 200
    response.status_code.should.equal(200)

    # And the response should be json
    response.headers.should.have.key('Content-Type').being.equal('application/json')

    # And the response data should contain an API token
    data = json.loads(response.data)
    data.should.have.key('api_token').being.a(basestring)
    api_token = data['api_token']

    # And the token should have a TTL in redis of less than 60 minutes
    minutes = 60
    user.api.get_token_ttl(api_token).should.be.lower_than(minutes * 60)
