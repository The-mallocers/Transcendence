import json
import uuid

from apps.chat.models import Messages, Rooms
from apps.client.models import Clients
from utils.enums import EventType, ResponseAction, ResponseError, RTables
from utils.websockets.channel_send import asend_group, asend_group_error
from utils.websockets.services.services import BaseServices, ServiceError

uuid_global_room = uuid.UUID('00000000-0000-0000-0000-000000000000')


class ChatService(BaseServices):
    async def init(self, client, *args) -> bool:
        await super().init(client)
        self.service_group = f'{EventType.CHAT.value}_{client.id}'
        self.channel_name = await self.redis.hget(name=RTables.HASH_CLIENT(client.id), key=str(EventType.CHAT.value))
        self.channel_name = self.channel_name.decode('utf-8')

        await self.channel_layer.group_add(RTables.GROUP_CHAT(uuid_global_room), self.channel_name)
        rooms = await Rooms.aget_room_id_by_client_id(client.id)
        for room in rooms:
            await self.channel_layer.group_add(RTables.GROUP_CHAT(room), self.channel_name)
        return True



    async def process_action(self, data, *args):
        if 'room_id' in data['data']['args'] and data['data']['args']['room_id'] == 'global':
            data['data']['args']['room_id'] = uuid_global_room
        return await super().process_action(data, *args)

    async def _handle_create_room(self, data, client: Clients):
        try:
            # Retrieve the target client
            target = await Clients.aget_client_by_id(data['data']['args']['target'])

            # Initial checks (target does not exist or same ID)
            if target is None:
                target = Clients.aget_client_by_username(data['data']['args']['target'])
                if target is None:
                    return await asend_group_error(self.service_group, ResponseError.TARGET_NOT_FOUND)

            if client.id == target.id:
                return await asend_group_error(self.service_group, ResponseError.SAME_ID)

            # Check for common rooms between admin and target
            rooms_admin = await Rooms.aget_room_id_by_client_id(client.id)
            rooms_target = await Rooms.aget_room_id_by_client_id(target.id)

            common_rooms = set(rooms_admin) & set(rooms_target)  # Optimized set intersection

            common_rooms.remove(uuid_global_room)

            if common_rooms:
                # Use an existing common room
                room = await Rooms.get_room_by_id(next(iter(common_rooms)))
            else:
                # Create a new room if no common room is found
                room = await Rooms.create_room()
                room.admin = client
                await room.asave()
                await room.add_client(client)
                await room.add_client(target)

            room_id = str(await Rooms.get_id(room))  # Store the value to avoid redundant async calls

            # Add both admin and target to the chat group
            await self.channel_layer.group_add(RTables.GROUP_CHAT(room_id), self.channel_name.decode('utf-8'))

            target_channel_name = await self.redis.hget(name=RTables.HASH_CLIENT(target.id), key=str(EventType.CHAT.value))
            if target_channel_name:
                await self.channel_layer.group_add(RTables.GROUP_CHAT(room_id), target_channel_name.decode('utf-8'))

            # Notify the admin that the room was created
            await asend_group(self.service_group, EventType.CHAT, ResponseAction.ROOM_CREATED, {'room_id': room_id})
        except json.JSONDecodeError as e:
            self._logger.error(f"JSON parsing error: {e}")

    async def _handle_send_message(self, data, client: Clients):
        try:
            # Validate request structure
            args = data.get('data', {}).get('args', {})
            message, room_id = args.get('message'), args.get('room_id')

            if not message or not room_id:
                raise ServiceError("Invalid JSON format: Missing 'message' or 'room_id'")

            # Retrieve room
            room = await Rooms.get_room_by_id(room_id)
            if room is None:
                return await asend_group_error(self.service_group, ResponseError.ROOM_NOT_FOUND)

            # Check if client is a member of the room
            if room.code not in await Rooms.aget_room_id_by_client_id(client.id):
                return await asend_group_error(self.service_group, ResponseError.NOT_ALLOWED)

            # Store the message
            await Messages.objects.acreate(sender=client, content=message, room=room)

            # Send the message to the group
            room_group = str(await Rooms.get_id(room))
            await asend_group(RTables.GROUP_CHAT(room_group), EventType.CHAT, ResponseAction.MESSAGE_RECEIVED, {
                'message': message,
                'sender': str(client.id),
                'room_id': str(room_group)
            })

        except ServiceError as e:
            self._logger.error(f"Service error: {e}")
            await asend_group_error(self.service_group, ResponseError.JSON_ERROR)
        except json.JSONDecodeError as e:
            self._logger.error(f"JSON parsing error: {e}")
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
                await asend_group_error(self.service_group, ResponseError.ROOM_NOT_FOUND)
                return

            messages = await Messages.aget_message_by_room(room)
            if not messages:
                await asend_group_error(self.service_group, ResponseError.NO_HISTORY)
                return

            # Sending messages in a single batch instead of multiple requests
            formatted_messages = [
                {"message": msg.content, "sender": str(await msg.get_sender_id()), "room_id": str(room_id)}
                for msg in messages
            ]
            await asend_group(self.service_group, EventType.CHAT, ResponseAction.HISTORY_RECEIVED,
                              {"messages": formatted_messages})

        except json.JSONDecodeError as e:
            self._logger.error(f"JSON parsing error: {e}")
        except ServiceError as e:
            self._logger.error(f"Service error: {e}")
            await asend_group_error(self.service_group, str(e))

    async def _handle_get_all_room_by_client(self, data, client: Clients):
        rooms = await Rooms.aget_room_id_by_client_id(client.id)
        formatted_messages = []
        for room in rooms:
            clients = await Rooms.get_usernames_by_room_id(room)
            players = []
            for Client in clients:
                player = Client
                if str(client.id) != await Rooms.get_client_id_by_username(Client):
                    players.append(player)
            formatted_messages.append({"room": str(room), "player": players})
        await asend_group(self.service_group, EventType.CHAT, ResponseAction.ALL_ROOM_RECEIVED, {"rooms": formatted_messages})

    async def disconnect(self, client):
        await self.channel_layer.group_discard(RTables.GROUP_CHAT(uuid_global_room), self.channel_name)
        rooms = await Rooms.aget_room_id_by_client_id(client.id)
        for room in rooms:
            await self.channel_layer.group_discard(RTables.GROUP_CHAT(room), self.channel_name)
