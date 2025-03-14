import logging
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Any

from django.conf import settings
from redis.asyncio import Redis

from utils.pong.enums import RequestAction


class ServiceError(Exception):
    def __init__(self, message='An error occured', code=400):
        self.message = message
        self.code = code
        super().__init__(f'{message}')

class BaseServices(ABC):
    def __init__(self):
        self._redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._initilized: bool = False

    @abstractmethod
    async def init(self, *args):
        pass

    @abstractmethod
    async def handle_disconnect(self, client):
        pass

    async def process_action(self, data: Dict[str, Any], *args):
        try:
            if not self._initilized:
                await self.init(*args)
            request_action = RequestAction(data['data']['action'])
            handler_method = getattr(self, f"_handle_{request_action.value}", None)

            if not handler_method or not callable(handler_method):
                raise ServiceError(f"Handler not found for this action : {request_action.value}")
            else:
                return await handler_method(data, *args)

        except ValueError:
            traceback.print_exc()
            raise ServiceError(f"This action is not valid: {data['data']['action']}")

        except ServiceError as e:
            raise e

