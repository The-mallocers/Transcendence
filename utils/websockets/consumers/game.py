from json import JSONDecodeError, loads

from utils.pong.enums import EventType, ResponseError
from utils.websockets.channel_send import asend_group_error
from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.game import GameService
from utils.websockets.services.matchmaking import MatchmakingService


class GameConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = MatchmakingService()

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = loads(text_data)
            if self.event_type is EventType.MATCHMAKING and data[
                'event'] == EventType.GAME.value:
                self.event_type = EventType(data['event'])
                self.service = GameService()
            return await super().receive(text_data, bytes_data)

        except JSONDecodeError as e:
            self._logger.error(e)
            await asend_group_error(self.client.id, ResponseError.JSON_ERROR)

    async def disconnect(self, close_code):
        pass
        # print('disconnect')
        # await self.service.handle_disconnect(self.client)
        # if self.service.game_manager is not None:
        #     print('disconnect in game service')
        #     await self.service.handle_disconnect(self.client)
        # await super().disconnect(close_code)
