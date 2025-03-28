import json
import logging
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from redis.asyncio import Redis

from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseError
from utils.websockets.channel_send import asend_group_error
from utils.websockets.services.services import ServiceError, BaseServices


class WsConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self._logger = logging.getLogger(self.__class__.__name__)

        self.client: Clients = None
        self.service: BaseServices = None
        self.event_type: EventType = None

    async def connect(self):
        logging.getLogger('websocket.client').info(f'New WebSocket connection from {self.scope["client"]}')
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)

        self.client: Clients = await Clients.get_client_by_id_async(query_params.get('id', ['default'])[0])

        await self.accept()
        if self.client is None:
            await self.channel_layer.group_add('consumer_error', self.channel_name)
            await asend_group_error('consumer_error', ResponseError.PLAYER_NOT_FOUND, close=True)
            return
        else:
            await self.channel_layer.group_add(str(self.client.id), self.channel_name)
            await self._redis.hset(name="consumers_channels", key=str(self.client.id), value=str(self.channel_name))

    async def disconnect(self, close_code):
        logging.getLogger('websocket.client').info(f'WebSocket disconnected with code {close_code}')
        await self._redis.hdel('consumers_channels', str(self.client.id))
        await self.channel_layer.group_discard(str(self.client.id), self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            self.event_type = EventType(data['event'])

            if not self.client:
                raise ServiceError("Client is not connected")

            if self.service.__class__.__name__ != self.event_type.value.capitalize() + 'Service':
                raise ServiceError("Service is not available")

            if self.event_type is EventType.MATCHMAKING:
                await self.service.process_action(data, self.client)

            if self.event_type is EventType.GAME:
                await self.service.process_action(data, self.client)

            if self.event_type is EventType.CHAT:
                await self.service.process_action(data, self.client)

            if self.event_type is EventType.TOURNAMENT:
                await self.service.process_action(data, self.client)

        except json.JSONDecodeError as e:
            self._logger.error(e)
            await asend_group_error(self.client.id, ResponseError.JSON_ERROR)

        except ServiceError as e:
            self._logger.error(e)
            await asend_group_error(self.client.id, ResponseError.SERVICE_ERROR, content=str(e))

    async def send_channel(self, event):
        message = event['message']
        close = event['close']
        await self.send(text_data=json.dumps(message, ensure_ascii=False), close=bool(close))
