# -*- coding: utf-8 -*-
from tests.functional.scenarios import api_test


@api_test
def test_index(context):
    ('/ should return the html index')

    response = context.http.get('/')

    response.status_code.should.equal(200)
    response.headers.should.have.key('Content-Type').being.equal(
        'text/html'
    )


@api_test
def test_index(context):
    ('/ should return the html index')

    response = context.http.get('/')

    response.status_code.should.equal(302)
    response.headers.should.have.key('Location').being.equal('http://localhost/in')
