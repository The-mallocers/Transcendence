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
        await channel_layer.group_add(str(player.id), channel_name.decode('utf-8'))

    async def _handle_start_chat(self, data, client: Clients, player: Player):
        try:
            if 'recipient_id' not in data['data']:
                raise KeyError("recipient_id is missing in data")

            recipient_id = data['data']['recipient_id']
            recipient_id = str(recipient_id)  # Convertir en chaîne de caractères

            # Vérifier si le destinataire est connecté
            recipient_channel = await self._redis.hget(name="consumers_channels", key=recipient_id)
            if not recipient_channel:
                # Le destinataire n'est pas connecté, renvoyer une erreur au client
                await send_group_error(client.id, ResponseError.PLAYER_NOT_FOUND, content="Recipient is not connected")
                return

            # Créer le nom du groupe de chat
            chat_group_name = f"chat_{min(str(player.id), recipient_id)}_{max(str(player.id), recipient_id)}"

            # Ajouter les deux clients au groupe de chat
            channel_layer = get_channel_layer()
            await channel_layer.group_add(chat_group_name, str(client.id))  # Expéditeur
            await channel_layer.group_add(chat_group_name, recipient_id)    # Destinataire

            # Envoyer une confirmation aux deux clients
            await send_group(client.id, EventType.CHAT, ResponseAction.CHAT_STARTED, content={
                'chat_group_name': chat_group_name,
                'recipient_id': recipient_id
            })
            await send_group(recipient_id, EventType.CHAT, ResponseAction.CHAT_STARTED, content={
                'chat_group_name': chat_group_name,
                'sender_id': player.id
            })
        except KeyError as e:
            self._logger.error(f"KeyError in _handle_start_chat: {e}")
            raise ServiceError("Invalid chat start format")
        except Exception as e:
            self._logger.error(f"Error in _handle_start_chat: {e}")
            raise ServiceError("Failed to start chat")

    async def _handle_send_message(self, data, client: Clients, player: Player):
        try:
            chat_group_name = data['data']['chat_group_name']
            message = data['data']['message']

            # Vérifier si le groupe de chat existe
            channel_layer = get_channel_layer()
            if not await self._redis.exists(f"group:{chat_group_name}"):  # Exemple de vérification
                raise ServiceError("Chat group does not exist")

            # Envoyer le message au groupe de chat
            await send_group(chat_group_name, EventType.CHAT, ResponseAction.MESSAGE, content={
                'sender_id': player.id,
                'message': message
            })
        except KeyError as e:
            self._logger.error(f"KeyError in _handle_send_message: {e}")
            raise ServiceError("Invalid message format")
        except Exception as e:
            self._logger.error(f"Error in _handle_send_message: {e}")
            raise ServiceError("Failed to send message")

    async def _handle_disconnect(self):
        pass