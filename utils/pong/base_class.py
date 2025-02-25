import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from redis.asyncio import Redis
from channels.layers import get_channel_layer
from django.conf import settings

from apps.player.models import Player
from utils.pong.enums import RequestAction, EventType

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
    async def init(self, player_id):
        pass

    async def process_action(self, data: Dict[str, Any], player: Player, *args):
        try:
            if not self._initilized:
                await self.init(player_id=player.id)
            request_action = RequestAction(data['data']['action'])
            handler_method = getattr(self, f"_handle_{request_action.value}", None)

            if not handler_method or not callable(handler_method):
                raise ServiceError(f"Handler not found for this action : {request_action.value}")
            else:
                return await handler_method(data, player, *args)

        except ValueError:
            raise ServiceError(f"This action is not a valid: {data['data']['action']}")

        except ServiceError as e:
            raise e

