# -*- coding: utf-8 -*-

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
    sqldb.drop_all()
    sqldb.create_all()


def reset_redis_database(context):
    context.redis = get_redis_connection()
    context.redis.flushall()


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
