import logging
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Any

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

        self.redis = None

    @abstractmethod
    async def init(self, *args) -> bool:
        self.redis = await RedisConnectionPool.get_async_connection(self.__class__.__name__)
        return True

    @abstractmethod
    async def handle_disconnect(self, client):
        pass

    async def process_action(self, data: Dict[str, Any], *args):
        try:
            if not self._initialized:
                self._initialized = await self.init(*args)
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
