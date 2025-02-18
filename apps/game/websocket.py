import json
import logging
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from redis.asyncio import Redis

from apps.game.services import MatchmakingService, GameService
from apps.player.manager import PlayerManager
from apps.player.models import PlayerGame, Player
from utils.pong.enums import RequestType
from utils.utils import ServiceError


class WebSocket(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self.game_service = GameService()
        self.matchmaking_service = MatchmakingService()
        self.player: Player = None

    async def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)

        self.player: Player = await PlayerManager.get_player_from_client_db(query_params.get('id', ['default'])[0])

        if self.player is None:
            await self.accept()
            await self.send(text_data=json.dumps({
                'error': 'Player not found'
            }), close=True)
            return

        await self.channel_layer.group_add(f'player_{str(self.player.pk)}', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.player is not None:
            await self.channel_layer.group_discard(f'player_{str(self.player.id)}', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            request_type = RequestType(data.get('type'))

            if request_type is RequestType.MATCHMAKING:
                await self.matchmaking_service.process_action(data, self.player)
            if request_type is RequestType.GAME:
                await self.game_service.process_action(data, self.player, None)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except ServiceError as e:
            await self.send(text_data=json.dumps({
                'error': f'{str(e)}'
            }))

    async def group_send(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
