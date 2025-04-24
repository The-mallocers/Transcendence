import asyncio
import logging
import os
import threading
from contextlib import contextmanager
from typing import Dict, Any

import redis
import redis.asyncio as aioredis
from django.conf import settings


class RedisConnectionPool:
    _logger = logging.getLogger(__name__)
    _pools: Dict[str, Dict[int, aioredis.Redis]] = {}
    _sync_pools: Dict[str, Dict[int, redis.Redis]] = {}
    _lock = threading.RLock()

    @classmethod
    def _get_connection_params(cls, alias: str = 'default') -> Dict[str, Any]:
        default_params = {
            'host': settings.REDIS_HOST,
            'port': settings.REDIS_PORT,
            'db': 0,
            'password': None,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True,
            'decode_responses': False,
        }

        try:
            if hasattr(settings, 'REDIS_CONNECTIONS'):
                redis_settings = settings.REDIS_CONNECTIONS.get(alias, {})
                default_params.update(redis_settings)

            if 'REDIS_URL' in os.environ:
                default_params['url'] = os.environ['REDIS_URL']
        except (AttributeError, ImportError):
            cls._logger.warning("Could not load Redis configuration from Django settings")

        return default_params

    @classmethod
    def _get_identifier(cls) -> int:
        try:
            task = asyncio.current_task()
            if task:
                return id(task)
        except (RuntimeError, AttributeError):
            pass

        return threading.get_ident()

    @classmethod
    async def get_async_connection(cls, alias: str = 'default') -> aioredis.Redis:
        identifier = cls._get_identifier()

        if alias not in cls._pools:
            cls._pools[alias] = {}

        if identifier not in cls._pools[alias]:
            params = cls._get_connection_params(alias)

            if 'url' in params:
                url = params.pop('url')
                connection = await aioredis.from_url(url, **params)
            else:
                host = params.pop('host', 'localhost')
                port = params.pop('port', 6380)
                db = params.pop('db', 0)
                password = params.pop('password', None)

                url = f"redis://{host}:{port}/{db}"
                connection = await aioredis.from_url(
                    url,
                    password=password,
                    **params
                )

            cls._pools[alias][identifier] = connection
            cls._logger.debug(f"Created new asynchronous Redis connection for alias: {alias}, context: {identifier}")

        return cls._pools[alias][identifier]

    @classmethod
    def get_sync_connection(cls, alias: str = 'default') -> redis.Redis:
        identifier = cls._get_identifier()

        if alias not in cls._sync_pools:
            cls._sync_pools[alias] = {}

        if identifier not in cls._sync_pools[alias]:
            params = cls._get_connection_params(alias)

            # Use the synchronous redis client, not the async one
            if 'url' in params:
                url = params.pop('url')
                connection = redis.from_url(url, **params)
            else:
                host = params.pop('host', 'localhost')
                port = params.pop('port', 6380)
                db = params.pop('db', 0)
                password = params.pop('password', None)

                url = f"redis://{host}:{port}/{db}"
                connection = redis.from_url(
                    url,
                    password=password,
                    **params
                )

            cls._sync_pools[alias][identifier] = connection
            cls._logger.debug(f"Created new Redis connection for alias: {alias}, context: {identifier}")

        return cls._sync_pools[alias][identifier]

    @classmethod
    @contextmanager
    def sync_client(cls, alias: str = 'default'):
        """
        Synchronous context manager for Redis connections.

        Usage:
            with RedisConnectionPool.sync_client() as redis:
                redis.json().get('key', '$.path')
        """
        connection = cls.get_sync_connection(alias)
        try:
            yield connection
        except Exception as e:
            cls._logger.error(f"Redis error: {str(e)}")
            raise
        finally:
            # No need to explicitly close synchronous Redis connections
            # They will be closed when the connection object is garbage collected
            pass

    @classmethod
    async def close_connection(cls, alias: str = 'default'):
        identifier = cls._get_identifier()

        with cls._lock:
            if alias in cls._pools and identifier in cls._pools[alias]:
                try:
                    await cls._pools[alias][identifier].close()
                    cls._logger.debug(f"Closed Redis connection for alias: {alias}, context: {identifier}")
                except Exception as e:
                    cls._logger.error(f"Error closing Redis connection: {str(e)}")
                finally:
                    del cls._pools[alias][identifier]

    @classmethod
    async def close_all_connections(cls):
        with cls._lock:
            for alias, connections in cls._pools.items():
                for identifier, connection in list(connections.items()):
                    try:
                        await connection.close()
                        cls._logger.debug(f"Closed Redis connection for alias: {alias}, context: {identifier}")
                    except Exception as e:
                        cls._logger.error(f"Error closing Redis connection: {str(e)}")
                    finally:
                        del connections[identifier]
            cls._pools.clear()
