from typing import Dict
from channels.layers import get_channel_layer
from apps.player.models import Player
from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseAction
from utils.websockets.channel_send import send_group
from utils.websockets.services.services import BaseServices, ServiceError  # Import correct
from utils.websockets.channel_send import send_group, send_group_error  # Ajoute send_group_error ici
from utils.pong.enums import EventType, ResponseAction, ResponseError  # Ajoute ResponseError ici
import json



class ChatService(BaseServices):
    async def init(self, client: Clients, player: Player):
        channel_layer = get_channel_layer()
        channel_name = await self._redis.hget(name="consumers_channels", key=str(client.id))
        # await channel_layer.group_add(str(player.id), channel_name.decode('utf-8'))

    async def _handle_send_message(self, data, client: Clients, player: Player):
        try:
            print("JSON reçu:", data)

            if 'data' in data and 'message' in data['data']:
                message = data['data']['message']
                channel_layer = get_channel_layer()
                await send_group('chat', EventType.CHAT, ResponseAction.SEND_MESSAGE, message)
            else:
                print("Erreur: Cle 'data' ou 'message' manquante dans le JSON reçu")
        except json.JSONDecodeError as e:
            print("Erreur parsing JSON:", e)

    async def _handle_disconnect(self):
        pass