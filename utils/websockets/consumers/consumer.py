import json
import logging
import traceback
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from redis.asyncio import Redis

from apps.client.models import Clients
from utils.enums import EventType, ResponseError, RTables
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
        path = self.scope['path']

        try:
            self.client: Clients = await Clients.aget_client_by_id(query_params.get('id', ['default'])[0])
            self.event_type = EventType(path.split('/')[2]) if len(path.split('/')) > 2 else None
            await self.accept()
            if await self._redis.hget(name=RTables.HASH_CLIENT(self.client.id), key=str(self.event_type.value)) is not None:
                raise ServiceError('You are already connected')
            else:
                await self.channel_layer.group_add(RTables.GROUP_CLIENT(self.client.id), self.channel_name)
                await self.channel_layer.group_add(f'{self.event_type.value}_{self.client.id}', self.channel_name)
                await self._redis.hset(name=RTables.HASH_CLIENT(self.client.id), key=str(self.event_type.value), value=str(self.channel_name))
                return True
        except AttributeError:
            await self.channel_layer.group_add(RTables.GROUP_ERROR, self.channel_name)
            await asend_group_error(RTables.GROUP_ERROR, ResponseError.CLIENT_NOT_FOUND, close=True)
            return False
        except ValueError:
            await self.channel_layer.group_add(RTables.GROUP_ERROR, self.channel_name)
            await asend_group_error(RTables.GROUP_ERROR, ResponseError.SERVICE_ERROR, content="Service is not available", close=True)
            return False
        except ServiceError:
            await self.channel_layer.group_add(RTables.GROUP_ERROR, self.channel_name)
            await asend_group_error(RTables.GROUP_ERROR, ResponseError.ALREADY_CONNECTED, close=True)
            return False

    async def disconnect(self, close_code):
        logging.getLogger('websocket.client').info(f'WebSocket disconnected with code {close_code}')
        await self.service.handle_disconnect(self.client)
        await self.channel_layer.group_discard(RTables.GROUP_ERROR, self.channel_name)
        self.event_type = EventType.GAME if self.event_type is EventType.MATCHMAKING else self.event_type
        if self.client:
            await self.channel_layer.group_discard(RTables.GROUP_CLIENT(self.client.id), self.channel_name)
            await self.channel_layer.group_discard(f'{self.event_type.value}_{self.client.id}', self.channel_name)
            await self._redis.hdel(RTables.HASH_CLIENT(self.client.id), str(self.event_type.value))

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if not self.client:
                raise ServiceError("Client is not connected")

            data = json.loads(text_data)
            self.event_type = EventType(data['event'])

            await self.service.process_action(data, self.client)

        except json.JSONDecodeError:
            self._logger.error(traceback.format_exc())
            await asend_group_error(RTables.GROUP_CLIENT(self.client.id), ResponseError.JSON_ERROR)

        except ServiceError as e:
            self._logger.error(f"{self.__class__.__name__} {traceback.format_exc()}")
            await asend_group_error(RTables.GROUP_CLIENT(self.client.id), ResponseError.SERVICE_ERROR, content=str(e))

        except Exception as e:
            self._logger.error(traceback.format_exc())
            await asend_group_error(RTables.GROUP_CLIENT(self.client.id), ResponseError.EXCEPTION, content=str(e), close=True)

    async def send_channel(self, event):
        message = event['message']
        close = event['close']
        await self.send(text_data=json.dumps(message, ensure_ascii=False), close=bool(close))
