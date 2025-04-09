from json import JSONDecodeError, loads
from urllib.parse import parse_qs

from apps.client.models import Clients
from utils.enums import EventType, ResponseError, RTables
from utils.websockets.channel_send import asend_group_error
from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.game import GameService
from utils.websockets.services.matchmaking import MatchmakingService


class GameConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = MatchmakingService()

    async def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)

        client: Clients = await Clients.get_client_by_id_async(query_params.get('id', ['default'])[0])

        if await self._redis.hget(name=RTables.HASH_CONSUMERS, key=str(client.id)) is not None:
            await self.accept()
            await self.channel_layer.group_add(RTables.GROUP_ERROR, self.channel_name)
            await asend_group_error(RTables.GROUP_ERROR, ResponseError.ALREADY_CONNECTED, close=True)
            return
        else:
            return await super().connect()


    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = loads(text_data)
            if self.event_type is EventType.MATCHMAKING and data[
                'event'] == EventType.GAME.value:
                self.event_type = EventType(data['event'])
                self.service = GameService()
            return await super().receive(text_data, bytes_data)

        except JSONDecodeError as e:
            self._logger.error(f'Json error: {e}')
            await asend_group_error(RTables.GROUP_CLIENT(self.client.id), ResponseError.JSON_ERROR)

    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        if self.client:
            await self.service.handle_disconnect(self.client)
