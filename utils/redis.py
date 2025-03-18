import os
from typing import Optional, Dict, Any, Union
import logging
from contextlib import contextmanager

import redis
from redis.exceptions import RedisError
import aioredis
import django
from django.conf import settings

logger = logging.getLogger(__name__)


class RedisConnectionPool:
    _sync_pools: Dict[str, redis.ConnectionPool] = {}
    _async_pools: Dict[str, aioredis.Redis] = {}

    @classmethod
    def get_connection_params(cls, alias: str = 'default') -> Dict[str, Any]:
        default_params = {
            'host': 'localhost',
            'port': 6379,
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
            elif hasattr(settings, 'CACHES') and 'redis' in settings.CACHES:
                cache_settings = settings.CACHES.get('redis', {}).get('OPTIONS', {})
                if 'CLIENT_CLASS' in cache_settings and 'redis' in cache_settings['CLIENT_CLASS'].lower():
                    default_params.update(cache_settings)
            
            if 'REDIS_URL' in os.environ:
                default_params['url'] = os.environ['REDIS_URL']
        except (AttributeError, ImportError):
            logger.warning("Could not load Redis configuration from Django settings")
        
        return default_params
    
    @classmethod
    def get_sync_connection(cls, alias: str = 'default') -> redis.Redis:
        if alias not in cls._sync_pools:
            params = cls.get_connection_params(alias)
            
            # If URL is provided, use from_url method
            if 'url' in params:
                url = params.pop('url')
                cls._sync_pools[alias] = redis.ConnectionPool.from_url(
                    url,
                    **{k: v for k, v in params.items() if k not in {'host', 'port', 'db', 'password'}}
                )
            else:
                cls._sync_pools[alias] = redis.ConnectionPool(**params)
                
            logger.debug(f"Created new Redis sync connection pool for alias: {alias}")
            
        return redis.Redis(connection_pool=cls._sync_pools[alias])
    
    @classmethod
    async def get_async_connection(cls, alias: str = 'default') -> aioredis.Redis:
        """
        Get an asynchronous Redis connection.
        
        Args:
            alias: The Redis connection alias defined in Django settings
            
        Returns:
            Asynchronous Redis client instance
        """
        if alias not in cls._async_pools:
            params = cls.get_connection_params(alias)
            
            # Create the appropriate connection URL for aioredis
            if 'url' in params:
                url = params.pop('url')
                cls._async_pools[alias] = await aioredis.from_url(
                    url,
                    **{k: v for k, v in params.items() if k not in {'host', 'port', 'db', 'password'}}
                )
            else:
                # Convert params to aioredis format
                host = params.pop('host')
                port = params.pop('port')
                db = params.pop('db')
                password = params.pop('password')
                
                url = f"redis://{host}:{port}/{db}"
                cls._async_pools[alias] = await aioredis.from_url(
                    url,
                    password=password,
                    **params
                )
                
            logger.debug(f"Created new Redis async connection pool for alias: {alias}")
        
        return cls._async_pools[alias]
    
    @classmethod
    @contextmanager
    def sync_client(cls, alias: str = 'default'):
        """
        Context manager for synchronous Redis connection.
        
        Args:
            alias: The Redis connection alias defined in Django settings
            
        Yields:
            Synchronous Redis client instance
        """
        client = None
        try:
            client = cls.get_sync_connection(alias)
            yield client
        except RedisError as e:
            logger.error(f"Redis error: {str(e)}")
            raise
        finally:
            # We don't close the connection here since it's managed by the pool
            pass
    
    @classmethod
    async def execute_async(cls, alias: str, coroutine_func, *args, **kwargs):
        """
        Execute an asynchronous Redis operation.
        
        Args:
            alias: The Redis connection alias defined in Django settings
            coroutine_func: Async function to call with the Redis client
            args: Arguments to pass to the coroutine function
            kwargs: Keyword arguments to pass to the coroutine function
            
        Returns:
            Result of the coroutine function
        """
        client = await cls.get_async_connection(alias)
        try:
            result = await coroutine_func(client, *args, **kwargs)
            return result
        except (RedisError, aioredis.RedisError) as e:
            logger.error(f"Redis async error: {str(e)}")
            raise
        # We don't close the connection here since it's managed by the pool
    
    @classmethod
    def close_all_connections(cls):
        """Close all Redis connections and clear the pools."""
        # Close sync connections
        for alias, pool in cls._sync_pools.items():
            try:
                pool.disconnect()
                logger.debug(f"Closed Redis sync connection pool for alias: {alias}")
            except Exception as e:
                logger.error(f"Error closing Redis sync connection pool for {alias}: {str(e)}")
        
        # Close async connections - this has to be done in an async context
        # This method should be called from an async context if async pools are used
        for alias, pool in cls._async_pools.items():
            try:
                pool.close()
                logger.debug(f"Closed Redis async connection pool for alias: {alias}")
            except Exception as e:
                logger.error(f"Error closing Redis async connection pool for {alias}: {str(e)}")
        
        cls._sync_pools = {}
        cls._async_pools = {}