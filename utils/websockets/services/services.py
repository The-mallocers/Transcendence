import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from channels.layers import get_channel_layer
from redis import Redis

from apps.client.models import Clients
from utils.enums import RequestAction
from utils.redis import RedisConnectionPool


class ServiceError(Exception):
    def __init__(self, message='An error occured', code=400):
        self.message = message
        self.code = code
        super().__init__(f'{message}')


class BaseServices(ABC):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._initialized: bool = False

        self.redis: Redis = None
        self.channel_layer = get_channel_layer()
        self.service_group = None

    @abstractmethod
    async def init(self, client: Clients, *args) -> bool:
        self.redis = await RedisConnectionPool.get_async_connection(self.__class__.__name__)
        return True

    @abstractmethod
    async def disconnect(self, client):
        # Base implementation for cleanup
        # Child classes should call this via super().disconnect(client)
        if self.service_group:
            # Remove from service group if it exists
            pass

    async def handle_disconnect(self, client):
        return await self.disconnect(client)

    async def process_action(self, data: Dict[str, Any], *args):
        try:
            handler_method = None
            if not self._initialized:
                self._initialized = await self.init(*args)
            request_action = RequestAction(data['data']['action'])
            if request_action:
                handler_method = getattr(self, f"_handle_{request_action.value}", None)
            if not handler_method or not callable(handler_method):

                raise ServiceError(f"CALLER CLASS: {self.__class__.__name__}, Handler not found for this action : {request_action.value}")
            else:
                return await handler_method(data, *args)

        except ValueError:
            raise ServiceError(f"This action is not valid: {data['data']['action']}")

        except ServiceError as e:
            raise e

        except Exception as e:
            raise e

    async def get_all_online_clients(self):
        client_keys = await self.redis.keys("client_*")
        # Decode because this gets us the results in bytes
        if client_keys and isinstance(client_keys[0], bytes):
            client_keys = [key.decode() for key in client_keys]
        return client_keys