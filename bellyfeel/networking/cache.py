# -*- coding: utf-8 -*-

from redis import StrictRedis
from redis import ConnectionPool


def get_redis_pool(redis_uri):
    return ConnectionPool.from_url(redis_uri)


def get_redis_connection(pool):
    return StrictRedis(connection_pool=pool)
