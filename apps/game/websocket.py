import json
import logging
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from redis.asyncio import Redis

from apps.game.services import MatchmakingService, GameService
from apps.player.manager import PlayerManager
from apps.player.models import Player
from utils.pong.base_class import ServiceError
from utils.pong.enums import EventType, ResponseError, ResponseAction


class WebSocket(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self._logger = logging.getLogger(self.__class__.__name__)
        self.game_service = GameService()
        self.matchmaking_service = MatchmakingService()
        self.player: Player = None

    async def connect(self):
        logging.getLogger('websocket.client').info(f'New WebSocket connection from {self.scope["client"]}')
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)

        self.player: Player = await PlayerManager.get_player_from_client_db(query_params.get('id', ['default'])[0])

        if self.player is None:
            await self.accept()
            await self.send_consumer_error(ResponseError.PLAYER_NOT_FOUND, close=True)
            return

        await self._redis.set(f"user_ws:{self.player.id}", self.channel_name)
        await self.channel_layer.group_add(f'player_{str(self.player.pk)}', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logging.getLogger('websocket.client').info(f'WebSocket disconnected with code {close_code}')
        if self.player is not None:
            await self.channel_layer.group_discard(f'player_{str(self.player.id)}', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            event_type = EventType(data['event'])

            if event_type is EventType.MATCHMAKING:
                await self.matchmaking_service.process_action(data, self.player)
            if event_type is EventType.GAME:
                await self.game_service.process_action(data, self.player, None)

        except json.JSONDecodeError:
            await self.send_consumer_error(ResponseError.JSON_ERROR)

        except ServiceError as e:
            self._logger.error(e)
            await self.send_consumer_error(ResponseError.SERVICE_ERROR, content=str(e))

    async def game_send(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    async def player_send(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    async def send_consumer_error(self, error_type: ResponseError, content = None, close: bool = False):
        await self.send(
            text_data=json.dumps({
                'event': EventType.ERROR,
                'data': {
                    'action': error_type.name,
                    'content': error_type.value + str(content),
                }
            }), close=close)

    async def send_consumer(self, event_type: EventType, msg_type: ResponseAction):
        await self.send(
            text_data=json.dumps({
                'event': event_type,
                'data': {
                    'action': msg_type.name,
                    'content': msg_type.value,
                }
            }))