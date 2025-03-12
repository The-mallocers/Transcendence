import json
import logging
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from redis.asyncio import Redis

from apps.player.manager import PlayerManager
from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseError
from utils.websockets.channel_send import send_group_error
from utils.websockets.services.game_service import GameService
from utils.websockets.services.matchmaking_service import MatchmakingService
from utils.websockets.services.services import ServiceError
from utils.websockets.services.chat_service import ChatService
from apps.chat.models import Rooms

class WebSocket(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self._logger = logging.getLogger(self.__class__.__name__)
        self.client: Clients = None

    async def connect(self):
        logging.getLogger('websocket.client').info(f'New WebSocket connection from {self.scope["client"]}')
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)

        self.client: Clients = await Clients.get_client_by_id_async(query_params.get('id', ['default'])[0])

        await self.accept()
        if self.client is None:
            await self.channel_layer.group_add('consumer_error', self.channel_name)
            await send_group_error('consumer_error', ResponseError.PLAYER_NOT_FOUND, close=True)
            return
        else:
            await self.channel_layer.group_add(str(self.client.id), self.channel_name)
            await self._redis.hset(name="consumers_channels", key=str(self.client.id), value=str(self.channel_name))

    async def disconnect(self, close_code):
        logging.getLogger('websocket.client').info(f'WebSocket disconnected with code {close_code}')
        if self.client is not None:
            await self.channel_layer.group_discard(str(self.client.id), self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if not self.client:
                raise ServiceError("Client is not connected")

            data = json.loads(text_data)
            event_type = EventType(data['event'])   

            if not hasattr(self, event_type.value + '_service'):
                raise ServiceError("Service is not available")

            if event_type is EventType.MATCHMAKING:
                player = await PlayerManager.get_player_from_client_db(self.client.id)
                await self.matchmaking_service.process_action(data, self.client, player)

            if event_type is EventType.GAME:
                player = await PlayerManager.get_player_from_client_db(self.client.id)
                await self.game_service.process_action(data, player)

            if event_type is EventType.CHAT:
                player = await PlayerManager.get_player_from_client_db(self.client.id)
                await self.chat_service.process_action(data, self.client)

        except json.JSONDecodeError as e:
            self._logger.error(e)
            await send_group_error(self.client.id, ResponseError.JSON_ERROR)

        except ServiceError as e:
            self._logger.error(e)
            await send_group_error(self.client.id, ResponseError.SERVICE_ERROR, content=str(e))

    async def send_channel(self, event):
        message = event['message']
        close = event['close']
        await self.send(text_data=json.dumps(message, ensure_ascii=False), close=bool(close))

class GameWebSocket(WebSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_service = GameService()
        self.matchmaking_service = MatchmakingService()

    async def connect(self):
        await super().connect()
        # Additional game-specific connection logic can go here

class ChatWebSocket(WebSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_service = ChatService()

    async def connect(self):
        await super().connect()
        # Additional chat-specific connection logic
        if self.client:
            # self.room_group_name = 'chat'
            # await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            rooms = await Rooms.get_room_id_by_client_id(self.client.id)
            for room in rooms:
                await self.channel_layer.group_add(str(room), self.channel_name)


