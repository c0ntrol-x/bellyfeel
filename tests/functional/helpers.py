# -*- coding: utf-8 -*-
from bellyfeel.sql import User


class APIClient(object):
    def __init__(self, http_client):
        self.http = http_client

    def create_active_user(self, email, password):
        new_user = User.create_with_password(
            email,
            password,
        ).activate_now()
        return new_user
