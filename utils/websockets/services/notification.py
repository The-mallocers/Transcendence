from django.forms import ValidationError

from apps.chat.models import Rooms, Messages
from apps.client.models import Clients
from utils.enums import EventType, ResponseAction, ResponseError, RTables
from utils.websockets.channel_send import asend_group, asend_group_error
from utils.websockets.services.services import BaseServices


class NotificationService(BaseServices):
    async def init(self, client, *args):
        self.service_group = f'{EventType.NOTIFICATION.value}_{client.id}'
        return await super().init(client)

    # Client is the person that want to add a friend to his friend list
    # Target is the friends to add
    # When i add a friend I put the client is to pending friend of the target person
    async def _handle_send_friend_request(self, data, client):
        # target is the client that I want to add
        target = await Clients.aget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await asend_group_error(self.service_group, ResponseError.USER_NOT_FOUND)
        friendTargetTable = await target.get_friend_table()

        # check if the friend ask is already in my pending list
        username = await client.aget_pending_request_by_client(target)
        # if the username exist in my pending list I accept it
        if username is not None:
            friend_request_data = {
                "event": "notification",
                "data": {
                    "action": "accept_friend_request",
                    "args": {
                        "target_name": data['data']['args']['target_name']
                    }
                }
            }
            return await self._handle_accept_friend_request(friend_request_data, client)

        askfriend = await friendTargetTable.add_pending_friend(client)
        # if I am already his friend 
        if askfriend is None:
            return await asend_group_error(self.service_group, ResponseError.USER_ALREADY_MY_FRIEND)
        await asend_group(RTables.GROUP_CLIENT(target.id),
                          EventType.NOTIFICATION,
                          ResponseAction.ACK_SEND_FRIEND_REQUEST,
                          {
                              "sender": str(client.id),
                              "username": await client.aget_profile_username()
                          })

    # client is the client that want to add the friend from his pending list
    # target is the friend pending
    async def _handle_accept_friend_request(self, data, client):
        target = await Clients.aget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await asend_group_error(self.service_group, ResponseError.USER_NOT_FOUND)
        try:
            friendTable = await client.get_friend_table()
            await friendTable.accept_pending_friend(target)
            friendTable = await target.get_friend_table()
            await friendTable.accept_other_friend(client)
            room = await Rooms.create_room()
            room.admin = client
            await room.asave()
            await room.add_client(client)
            await room.add_client(target)

            await asend_group(self.service_group, EventType.NOTIFICATION,
                              ResponseAction.ACK_ACCEPT_FRIEND_REQUEST_HOST,
                              {
                                  "sender": str(target.id),
                                  "username": await target.aget_profile_username()
                              })

            await asend_group(RTables.GROUP_CLIENT(target.id), EventType.NOTIFICATION,
                              ResponseAction.ACK_ACCEPT_FRIEND_REQUEST,
                              {
                                  "sender": str(client.id),
                                  "username": await client.aget_profile_username(),
                                  "room": str(room.id)
                              })

        except:
            return await asend_group_error(self.service_group, ResponseError.USER_ALREADY_FRIEND_OR_NOT_PENDING_FRIEND)

    async def _handle_refuse_friend_request(self, data, client):
        target = await Clients.aget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await asend_group_error(self.service_group, ResponseError.USER_NOT_FOUND)
        try:
            # refuse the pending friend request
            friendTable = await client.get_friend_table()
            await friendTable.refuse_pending_friend(target)
            await asend_group(self.service_group, EventType.NOTIFICATION,
                              ResponseAction.ACK_REFUSE_FRIEND_REQUEST,
                              {
                                  "sender": str(target.id),
                                  "username": await target.aget_profile_username()
                              })
        except:
            return await asend_group_error(self.service_group, ResponseError.USER_ALREADY_FRIEND_OR_NOT_PENDING_FRIEND, )

    async def _handle_delete_friend(self, data, client):
        target = await Clients.aget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await asend_group_error(self.service_group, ResponseError.USER_NOT_FOUND)

        try:
            client_friend_table = await client.get_friend_table()
            await client_friend_table.remove_friend(target)

            target_friend_table = await target.get_friend_table()
            await target_friend_table.remove_friend(client)
            await asend_group(self.service_group,
                              EventType.NOTIFICATION,
                              ResponseAction.ACK_DELETE_FRIEND_HOST,
                              {
                                  "sender": str(target.id),
                                  "username": await target.aget_profile_username()
                              })

            await asend_group(RTables.GROUP_CLIENT(target.id),
                              EventType.NOTIFICATION,
                              ResponseAction.ACK_DELETE_FRIEND,
                              {
                                  "sender": str(client.id),
                                  "username": await client.aget_profile_username()
                              })
            # get the room to delete
            room = await Rooms.aget_room_by_client_id(client.id)
            if room is None:
                return
            # First delete all messages corresponding to the two users
            await Messages.adelete_all_messages_by_room_id(room)
            # Then delete the two user from the room
            await Rooms.adelete_all_user_by_room_id(room)
            # Then delete the room
            await room.adelete_room()
        except ValidationError:
            return await asend_group_error(self.service_group, ResponseError.NOT_FRIEND)
        except Exception as e:
            return await asend_group_error(self.service_group, ResponseError.INTERNAL_ERROR)

    async def _handle_ask_duel(self, data, client):
        target = await Clients.aget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.USER_NOT_FOUND)
        try:
            return await asend_group(RTables.GROUP_CLIENT(target.id),
                                    EventType.NOTIFICATION,
                                    ResponseAction.ACK_ASK_DUEL,
                                    {
                                        "sender": str(client.id),
                                        "username": await client.aget_profile_username() 
                                    })
        except Exception as e:
            print(repr(e))
            return await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.INTERNAL_ERROR)

    async def _handle_accept_duel(self, data, client):
        code = data['data']['args']['code']
        if await Clients.acheck_in_queue(client, self.redis):
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
        if not await self.redis.exists(RTables.HASH_DUEL_QUEUE(code)):
            return await asend_group_error(self.service_group, ResponseError.DUEL_NOT_EXIST)
        if await self.redis.hexists(RTables.HASH_DUEL_QUEUE(code), str(client.id)) is False:
            return await asend_group_error(self.service_group, ResponseError.NOT_INVITED)
        else:
            if await self.redis.hget(RTables.HASH_DUEL_QUEUE(code), str(client.id)) == 'True':
                return await asend_group_error(self.service_group, ResponseError.ALREADY_JOIN_DUEL)
            else:
                await self.redis.hset(RTables.HASH_DUEL_QUEUE(code), str(client.id), 'True')
                await asend_group(self.service_group, EventType.MATCHMAKING, ResponseAction.DUEL_JOIN)

    async def _handle_pending_duels(self, data, client):
        if await Clients.acheck_in_queue(client, self.redis):
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)

        pending_duels = []
        async for key in self.redis.scan_iter(match=f"{RTables.HASH_DUEL_QUEUE('*')}"):
            if await self.redis.hexists(key, str(client.id)):
                duel_status = await self.redis.hget(key, str(client.id))
                duel_code = key.decode().split(":")[-1]
                pending_duels.append({
                    "code": duel_code,
                    "status": duel_status == 'True'
                })

        await asend_group(self.service_group,
                          EventType.NOTIFICATION,
                          ResponseAction.ACK_PENDING_DUELS,
                          {"pending_duels": pending_duels})

    async def _handle_refuse_duel(self, data, client):
        code = data['data']['args']['code']
        if not await self.redis.exists(RTables.HASH_DUEL_QUEUE(code)):
            return await asend_group_error(self.service_group, ResponseError.DUEL_NOT_EXIST)
        if await self.redis.hexists(RTables.HASH_DUEL_QUEUE(code), str(client.id)) is False:
            return await asend_group_error(self.service_group, ResponseError.NOT_INVITED)
        else:
            if await self.redis.hget(RTables.HASH_DUEL_QUEUE(code), str(client.id)) == 'True':
                return await asend_group_error(self.service_group, ResponseError.CANNOT_REFUSE_DUEL)
            else:
                await self.redis.delete(RTables.HASH_DUEL_QUEUE(code))
                players = await self.redis.hgetall(RTables.HASH_DUEL_QUEUE(code))
                opponent_id = None
                async for key, value in players.items():
                    decoded_key = key.decode()
                    if decoded_key != str(client.id):
                        opponent_id = decoded_key
                        break
                await asend_group(self.service_group, EventType.NOTIFICATION, ResponseAction.REFUSED_DUEL)
                await asend_group(RTables.GROUP_NOTIF(opponent_id), EventType.NOTIFICATION, ResponseAction.DUEL_REFUSED)
    
    async def disconnect(self, client):
        pass
