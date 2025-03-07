from typing import Dict
from channels.layers import get_channel_layer
from apps.player.models import Player
from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseAction
from utils.websockets.channel_send import send_group
from utils.websockets.services.services import BaseServices, ServiceError  # Import correct
from utils.websockets.channel_send import send_group, send_group_error  # Ajoute send_group_error ici
from utils.pong.enums import EventType, ResponseAction, ResponseError  # Ajoute ResponseError ici

class ChatService(BaseServices):
    async def init(self, client: Clients, player: Player):
        channel_layer = get_channel_layer()
        channel_name = await self._redis.hget(name="consumers_channels", key=str(client.id))
        # await channel_layer.group_add(str(player.id), channel_name.decode('utf-8'))

    async def _handle_start_chat(self, data: Dict, player: Player):
        try:
          # Charger le JSON
            text_data_json = json.loads(text_data)
            
            # Debug: Afficher la structure du JSON reçu
            print("JSON reçu:", text_data_json)
            
            # Vérifier si 'data' existe bien dans le JSON
            if 'data' in text_data_json and 'message' in text_data_json['data']:
                message = text_data_json['data']['message']
                # print(f"Received message: {message}")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message
                    }
                )
            else:
                print("Erreur: Clé 'data' ou 'message' manquante dans le JSON reçu")
        except json.JSONDecodeError as e:
            print("Erreur de parsing JSON:", e)

        async def chat_message(self, event):
            message = event['message']
            await self.send(text_data=json.dumps({
                'message': message
            }))

    async def _handle_disconnect(self):
        pass