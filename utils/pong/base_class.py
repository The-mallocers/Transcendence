import logging
from abc import ABC
from typing import Dict, Any

from redis.asyncio import Redis
from channels.layers import get_channel_layer
from django.conf import settings

from apps.player.models import Player
from utils.pong.enums import RequestAction, SendType
from utils.utils import ServiceError


class BaseServices(ABC):
    def __init__(self):
        self.redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self.player_channel = None

    async def process_action(self, data: Dict[str, Any], player: Player, *args):
        request_action = RequestAction(data.get('action'))
        self.player_channel = f'player_{str(player.pk)}'

        handler_method = getattr(self, f"_handle_{request_action.value}", None)

        if handler_method and callable(handler_method):
            return await handler_method(data, player, *args)
        else:
            logging.error(f"Handler not found for this action : {request_action.value}")
            raise ServiceError(f"Handler not found for this action : {request_action.value}")

    async def send_to_group(self, send_type: SendType, payload):
        channel_layers = get_channel_layer()
        await channel_layers.group_send(
            self.player_channel,
            {
                'type': 'group_send',
                'message': {
                    'send_type': send_type.value,
                    'payload': payload
                }
            }
        )