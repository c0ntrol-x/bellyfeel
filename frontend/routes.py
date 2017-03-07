# -*- coding: utf-8 -*-
from datetime import datetime
from plant import Node
from flask import request
from p4rr0t007.web import Application

here = Node(__file__).dir
server = Application(here, static_path='/dist', template_folder=here.path, static_folder=here.join('dist'))


@server.route('/')
def index():
    return server.template_response("index.html", {
        'user_token': request.cookies.get('bellyfeel_token') or ''
    })


@server.route('/api/login')
def projects():
    return server.json_response([
        {
            "name": "Foo",
            "description": "The foo of the bar",
            "tags": ["test", "local"],
            "url": "http://foo.co",
            "last_build": datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"),
        },
        {
            "name": "Bar",
            "description": "The bar whence the foo belongs",
            "tags": ["example", "local"],
            "url": "http://bar.foo",
            "last_build": datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"),
        },
    ], 200)


if __name__ == '__main__':
    server.run(debug=True)
