from json import JSONDecodeError, loads

from apps.client.models import Clients
from utils.enums import EventType, ResponseError, RTables
from utils.websockets.channel_send import asend_group_error
from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.game import GameService
from utils.websockets.services.matchmaking import MatchmakingService
from utils.websockets.services.services import ServiceError


class GameConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = MatchmakingService()

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = loads(text_data)
            if self.event_type is EventType.MATCHMAKING and data['event'] == EventType.GAME.value:
                self.event_type = EventType(data['event'])
                self.service = GameService()

            if data['event'] == EventType.GAME.value and await self._redis.hget(name=RTables.HASH_MATCHES, key=str(self.client.id)) is None:
                raise ServiceError('You are not in game')
            return await super().receive(text_data, bytes_data)

        except ServiceError as e:
            await asend_group_error(RTables.GROUP_CLIENT(self.client.id), ResponseError.NO_GAME, str(e))

        except JSONDecodeError as e:
            self._logger.error(f'Json error: {e}')
            await asend_group_error(RTables.GROUP_CLIENT(self.client.id), ResponseError.JSON_ERROR)

