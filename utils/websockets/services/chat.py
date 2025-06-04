import django.db
import json
import uuid
import html

from apps.chat.models import Messages, Rooms
from apps.client.models import Clients
from utils.enums import EventType, ResponseAction, ResponseError, RTables
from utils.websockets.channel_send import asend_group, asend_group_error
from utils.websockets.services.services import BaseServices, ServiceError
from django.db import transaction
from django.utils import timezone

uuid_global_room = uuid.UUID('00000000-0000-0000-0000-000000000000')
MAX_MESSAGE_LENGTH = 200

class ChatService(BaseServices):
    async def init(self, client, *args) -> bool:
        await super().init(client)
        self.service_group = f'{EventType.CHAT.value}_{client.id}'
        self.channel_name = await self.redis.hget(name=RTables.HASH_CLIENT(client.id), key=str(EventType.CHAT.value))
        self.channel_name = self.channel_name.decode('utf-8')

        # await self.channel_layer.group_add(RTables.GROUP_CHAT(uuid_global_room), self.channel_name)
        rooms = await Rooms.aget_room_id_by_client_id(client.id)
        for room in rooms:
            await self.channel_layer.group_add(RTables.GROUP_CHAT(room), self.channel_name)
        return True

    async def _handle_send_message(self, data, client: Clients):
        try:
            # Validate request structure
            args = data.get('data', {}).get('args', {})
            message, room_id = args.get('message'), args.get('room_id')

            if not message or not room_id:
                raise ServiceError("Invalid JSON format: Missing 'message' or 'room_id'")

             # Check message length
            if len(message) > MAX_MESSAGE_LENGTH:
                return await asend_group_error(self.service_group, ResponseError.INVALID_REQUEST, 
                                            f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters")
            
            # Sanitize the message content
            message = html.escape(message)

            # Retrieve room
            room = await Rooms.get_room_by_id(room_id)
            if room is None:
                return await asend_group_error(self.service_group, ResponseError.ROOM_NOT_FOUND)

            # Check if client is a member of the room
            if room.id not in await Rooms.aget_room_id_by_client_id(client.id):
                return await asend_group_error(self.service_group, ResponseError.NOT_ALLOWED)

            target = await room.aget_target_by_room_id(client)
            if target:
                # dans le cas ou j'envoie un message a un user bloqué
                player = await client.get_friend_table()
                if await player.user_is_block(target):
                    return await asend_group(RTables.GROUP_CHAT(str(client.id)), EventType.CHAT,
                                             ResponseAction.ERROR_MESSAGE_USER_BLOCK,
                                             {
                                                 'message': "You can't send messages to block user",
                                                 'sender': str(client.id),
                                                 'room_id': str(room.id)
                                             })

                # dans le cas ou j'envoie un message à un utilisateur qui m'a bloqué
                player = await target.get_friend_table()
                if await player.user_is_block(client):
                    return await asend_group(RTables.GROUP_CHAT(str(client.id)), EventType.CHAT,
                                             ResponseAction.ERROR_MESSAGE_USER_BLOCK,
                                             {
                                                 'message': "You can't send messages to block user",
                                                 'sender': str(client.id),
                                                 'room_id': str(room.id)
                                             })
            # await Messages.aset_message(client, room, message)
            
            timestamp = timezone.now()
            await Messages.objects.acreate(sender=client, content=message, room=room, send_at=timestamp)

            # Send the message to the group  
            room_group = str(await Rooms.get_id(room))
            await asend_group(RTables.GROUP_CHAT(room_group), EventType.CHAT, ResponseAction.MESSAGE_RECEIVED, {
                'message': message,
                'sender': str(client.id),
                'username': await client.aget_profile_username(),
                'room_id': str(room_group),
            })

            username = await client.aget_profile_username() if target else "Unknown User"

            await asend_group(RTables.GROUP_NOTIF(str(target.id)), EventType.NOTIFICATION, ResponseAction.NEW_MESSAGE, {
                    "sender_id": username,
            })

        except ServiceError as e:
            await asend_group_error(self.service_group, ResponseError.JSON_ERROR)
        except json.JSONDecodeError as e:
            await asend_group_error(self.service_group, ResponseError.JSON_ERROR)

    async def _handle_get_history(self, data, client: Clients):
        try:
            # Extracting data in a cleaner way
            args = data.get("data", {}).get("args", {})
            room_id = args.get("room_id")

            if not room_id:
                raise ServiceError("Invalid format JSON: room_id missing")

            # Fetching the room and its messages
            room = await Rooms.get_room_by_id(room_id)
            if not room:
                return await asend_group_error(self.service_group, ResponseError.ROOM_NOT_FOUND)

            target = await room.aget_target_by_room_id(client)

            messages = await Messages.aget_message_by_room(room, target)
            if not messages:
                await asend_group_error(self.service_group, ResponseError.NO_HISTORY, {
                    "username": str(await target.aget_profile_username())
                })
                return
            
            # set has true all the messages is_read
            await Messages.objects.filter(room=room, sender=target, is_read=False).aupdate(is_read=True)

            # Sending messages in a single batch instead of multiple requests
            formatted_messages = [
                {"message": msg.content, "sender": str(await msg.get_sender_id()), "room_id": str(room_id)}
                for msg in messages
            ]
            await asend_group(self.service_group, EventType.CHAT, ResponseAction.HISTORY_RECEIVED,
                              {"messages": formatted_messages,
                               "username": str(await target.aget_profile_username())})

        except json.JSONDecodeError as e:
            self._logger.error(f"JSON parsing error: {e}")
        except ServiceError as e:
            self._logger.error(f"Service error: {e}")
            await asend_group_error(self.service_group, str(e))

    async def _handle_get_all_room_by_client(self, data, client: Clients):
        rooms = await Rooms.aget_room_id_by_client_id(client.id)
        formatted_messages = []
        for room_id in rooms:
            room = await Rooms.get_room_by_id(room_id)
            if room:
                users = await Rooms.get_user_info_by_room_id(room_id)
                other_users = [user for user in users if str(user['id']) != str(client.id)]
                friend = await client.get_friend_table()
                if other_users:
                    for user in other_users:
                        status = "Unblock" if await friend.ais_blocked(user['id']) else "Block"
                        formatted_messages.append({
                            'room': str(room_id),
                            'unread_messages': await Messages.aget_unread_messages(room_id, user['id']),
                            'player': [{
                                'id': user['id'],
                                'username': user['username'],
                                'profile_picture': user['profile_picture'],
                                'status': status
                            }]
                        })
        await asend_group(self.service_group, 
                        EventType.CHAT, 
                        ResponseAction.ALL_ROOM_RECEIVED, 
                        {"rooms": formatted_messages})
        
    async def _handle_ping(self, data, client):
        return await asend_group(self.service_group, EventType.CHAT, ResponseAction.PONG)

    async def disconnect(self, client):
        await self.channel_layer.group_discard(RTables.GROUP_CHAT(uuid_global_room), self.channel_name)
        rooms = await Rooms.aget_room_id_by_client_id(client.id)
        for room in rooms:
            await self.channel_layer.group_discard(RTables.GROUP_CHAT(room), self.channel_name)
