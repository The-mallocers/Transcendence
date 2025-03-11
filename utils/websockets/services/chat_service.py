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

from asgiref.sync import sync_to_async
from apps.chat.models import Rooms



class ChatService(BaseServices):
    async def init(self, client: Clients):
        self.channel_layer = get_channel_layer()
        self.channel_name = await self._redis.hget(name="consumers_channels", key=str(client.id))
        # await channel_layer.group_add(str(player.id), channel_name.decode('utf-8'))

    async def _handle_create_room(self, data, admin: Clients):
        try:
            target = await Clients.get_client_by_id_async(data['data']['args']['target'])

            if target is None:
                raise ServiceError('Target not found')
            
            rooms_admin = await Rooms.get_room_id_by_client_id(admin.id)
            rooms_target = await Rooms.get_room_id_by_client_id(target.id)

            common_rooms = set(rooms_admin).intersection(set(rooms_target))
            
            if common_rooms:
                #if room was common with admin and target, we don't create new room but we set the 'room' to common room we found
                room = await Rooms.get_room_by_id(next(iter(common_rooms)))
            else:
                #here we create new room when no common room was found
                room = await Rooms.create_room()
                room.admin = admin
                await room.asave()
                await room.add_client(admin)
                await room.add_client(target)

            await self.channel_layer.group_add(str(await Rooms.get_id(room)), self.channel_name.decode('utf-8'))
            target_channel_name = await self._redis.hget(name="consumers_channels", key=str(target.id))
            if target_channel_name:
                await self.channel_layer.group_add(str(await Rooms.get_id(room)), target_channel_name.decode('utf-8'))

            await send_group(admin.id, EventType.CHAT, ResponseAction.ROOM_CREATED)


        except json.JSONDecodeError as e:
            print("Erreur parsing JSON:", e)
            

    async def _handle_send_message(self, data, client: Clients):
        try:
            if 'data' in data and 'args' in data['data'] and 'message' in data['data']['args'] and 'room_id' in data['data']['args']:
                message = data['data']['args']['message']
                room = await Rooms.get_room_by_id(data['data']['args']['room_id'])
                # channel_layer = get_channel_layer()
                await send_group(await Rooms.get_id(room), EventType.CHAT, ResponseAction.MESSAGE_RECEIVED, message)
            else:
                raise ServiceError("Invalid format JSON")
        except json.JSONDecodeError as e:
            print("Erreur parsing JSON:", e)

    async def _handle_disconnect(self):
        pass