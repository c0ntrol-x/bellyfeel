# -*- coding: utf-8 -*-
import functools
from sure import scenario
from bellyfeel.application import server
from bellyfeel.sql import db as sqldb
from bellyfeel.sql import get_redis_connection


def turn_on_api_client(context):
    context.http = server.test_client()


def turn_off_api_client(context):
    pass


def reset_sql_database(context):
    context.sql = sqldb
    sqldb.metadata.drop_all(sqldb.engine)
    sqldb.metadata.create_all(sqldb.engine)


def reset_redis_database(context):
    context.redis = get_redis_connection()
    context.redis.flushall()


def session_url(*ctx_args, **ctx_kw):
    def contextual(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            with server.test_request_context(*ctx_args, **ctx_kw):
                return func(*args, **kw)

        return api_test(wrapper)

    return contextual


api_test = scenario(
    [
        turn_on_api_client,
        reset_redis_database,
        reset_sql_database,
    ],
    [
        turn_off_api_client,
        reset_redis_database,
        reset_sql_database,
    ]
)
