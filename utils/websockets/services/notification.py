from asgiref.sync import sync_to_async
from django.forms import ValidationError
from channels.db import database_sync_to_async

from apps.chat.models import Rooms, Messages
from apps.client.models import Clients
from utils.enums import EventType, ResponseAction, ResponseError, RTables
from utils.util import create_game_id, get_all_online_clients, aget_all_online_clients
from utils.websockets.channel_send import asend_group, asend_group_error
from utils.websockets.services.services import BaseServices


class NotificationService(BaseServices):
    async def init(self, client, *args):
        await super().init(client)
        self.service_group = f'{EventType.NOTIFICATION.value}_{client.id}'
        username = await self.get_username(client)
        online_clients = await aget_all_online_clients(self.redis)
        for client in online_clients:
            await asend_group(client, EventType.NOTIFICATION, ResponseAction.ACK_ONLINE_STATUS,{
                    "username": username,
                    "online": True
                })
        return True

    @database_sync_to_async
    def get_username(self, client):
        return client.profile.username

    # Client is the person that want to add a friend to his friend list
    # Target is the friends to add
    # When i add a friend I put the client is to pending friend of the target person
    async def _handle_send_friend_request(self, data, client):
        # target is the client that I want to add
        target = await Clients.aget_client_by_username(data.get('data').get('args').get('target_name'))
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
                        "target_name": data.get('data').get('args').get('target_name')
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
        target = await Clients.aget_client_by_username(data.get('data').get('args').get('target_name'))
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
            clientFriendTable = await client.get_friend_table()
            targetFriendTable = await target.get_friend_table()
            
            clientBlock = "Block"
            targetBlock = "Block"
            
            if clientFriendTable and await clientFriendTable.user_is_block(target) is True:
                clientBlock = "Unblock"
            if targetFriendTable and await targetFriendTable.user_is_block(client) is True:
                targetBlock = "Unblock"
                
            profile_picture_source = await client.aget_profile_by_user()
            profile_picture_target = await target.aget_profile_by_user()

            await asend_group(self.service_group, EventType.NOTIFICATION,
                              ResponseAction.ACK_ACCEPT_FRIEND_REQUEST_HOST,
                              {
                                "sender": str(target.id),
                                "username": await target.aget_profile_username(),
                                "room": str(room.id),
                                "textBlock": clientBlock,
                                "profile_picture": profile_picture_target
                              })

            await asend_group(RTables.GROUP_NOTIF(target.id), EventType.NOTIFICATION,
                              ResponseAction.ACK_ACCEPT_FRIEND_REQUEST,
                              {
                                "sender": str(client.id),
                                "username": await client.aget_profile_username(),
                                "room": str(room.id),
                                "textBlock": targetBlock,
                                "profile_picture": profile_picture_source
                              })

        except:
            return await asend_group_error(self.service_group, ResponseError.USER_ALREADY_FRIEND_OR_NOT_PENDING_FRIEND)

    async def _handle_refuse_friend_request(self, data, client):
        target = await Clients.aget_client_by_username(data.get('data').get('args').get('target_name'))
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
        target = await Clients.aget_client_by_username(data.get('data').get('args').get('target_name'))
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
            room = await Rooms.Aget_room_by_client_id(client.id)
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

    # ====================================DUELS=========================================

    async def _handle_create_duel(self, data, client: Clients):
        # ── Target Check ──────────────────────────────────────────────────────────── #
        target = await Clients.aget_client_by_id(data.get('data').get('args').get('target'))
        if target is None:
            return await asend_group_error(self.service_group, ResponseError.TARGET_NOT_FOUND)
        target_online = await self.redis.hget(RTables.HASH_CLIENT(target.id), str(EventType.NOTIFICATION.value))
        if not target_online:
            return await asend_group_error(self.service_group, ResponseError.USER_OFFLINE)
        if target.id == client.id:
            return await asend_group_error(self.service_group, ResponseError.DUEL_HIMSELF)
        client_friend_table = await client.get_friend_table()
        target_firend_table = await target.get_friend_table()
        client_blocked_target = await client_friend_table.ais_blocked(target.id)
        target_blocked_client = await target_firend_table.ais_blocked(client.id)
        if client_blocked_target or target_blocked_client:
            return await asend_group_error(self.service_group, ResponseError.BLOCKED_USER)
        target_queues = await Clients.acheck_in_queue(target, self.redis)
        if target_queues is not RTables.HASH_G_QUEUE.value and target_queues is not None:
            if await self.redis.hexists(target_queues, str(target.id)):
                return await asend_group_error(self.service_group, ResponseError.ALREADY_INVITED)
        # ── Client Check ──────────────────────────────────────────────────────────── #
        queues = await Clients.acheck_in_queue(client, self.redis)
        if queues:
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
        if await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id)) is not None:
            return await asend_group_error(self.service_group, ResponseError.ALREAY_IN_GAME)
        else:
            duel_code = await sync_to_async(create_game_id)()
            await self.redis.hset(name=RTables.HASH_DUEL_QUEUE(duel_code), key=str(client.id), value=str(True))
            await self.redis.hset(name=RTables.HASH_DUEL_QUEUE(duel_code), key=str(target.id), value=str(False))
            await asend_group(self.service_group, EventType.NOTIFICATION, ResponseAction.DUEL_CREATED, {
                'code': duel_code,
                'opponent': await target.aget_profile_username(),
                'hostimage': client.profile.profile_picture.url,
                'opponentImage': target.profile.profile_picture.url
            })
            return await asend_group(RTables.GROUP_NOTIF(target.id), EventType.NOTIFICATION,
                                     ResponseAction.ACK_ASK_DUEL,
                                     {
                                         "sender": str(client.id),
                                         "username": await client.aget_profile_username(),
                                         'code': duel_code,
                                        'hostimage': target.profile.profile_picture.url,
                                        'opponentImage': client.profile.profile_picture.url
                                     })

    async def _handle_accept_duel(self, data, client):
        code = data.get('data').get('args').get('code')
        target_name = data.get('data').get('args').get('username')
        if code is None or target_name is None:
            return await asend_group_error(self.service_group, ResponseError.JSON_ERROR)
        target = await Clients.aget_client_by_username(target_name)
        if await Clients.acheck_in_queue(client, self.redis):
            return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)
        if not await self.redis.exists(RTables.HASH_DUEL_QUEUE(code)):
            return await asend_group_error(self.service_group, ResponseError.DUEL_NOT_EXIST, {"opponent": target_name})
        if await self.redis.hexists(RTables.HASH_DUEL_QUEUE(code), str(client.id)) is False:
            return await asend_group_error(self.service_group, ResponseError.NOT_INVITED)
        else:
            if await self.redis.hget(RTables.HASH_DUEL_QUEUE(code), str(client.id)) == 'True':
                return await asend_group_error(self.service_group, ResponseError.ALREADY_JOIN_DUEL)
            else:
                await self.redis.hset(RTables.HASH_DUEL_QUEUE(code), str(client.id), 'True')
                await asend_group(self.service_group, EventType.NOTIFICATION, ResponseAction.DUEL_JOIN, {
                                         "opponent": await target.aget_profile_username(),
                                     })
                await asend_group(RTables.GROUP_NOTIF(target.id), EventType.NOTIFICATION, ResponseAction.DUEL_JOIN)

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
        code = data.get('data').get('args').get('code')
        target_name = data.get('data').get('args').get('username')
        if code is None or target_name is None:
            return await asend_group_error(self.service_group, ResponseError.JSON_ERROR)
        if not await self.redis.exists(RTables.HASH_DUEL_QUEUE(code)):
            return await asend_group_error(self.service_group, ResponseError.DUEL_NOT_EXIST, {"opponent": target_name})
        if await self.redis.hexists(RTables.HASH_DUEL_QUEUE(code), str(client.id)) is False:
            return await asend_group_error(self.service_group, ResponseError.NOT_INVITED)
        else:
            if await self.redis.hget(RTables.HASH_DUEL_QUEUE(code), str(client.id)) == 'True':
                return await asend_group_error(self.service_group, ResponseError.CANNOT_REFUSE_DUEL)
            else:
                players = await self.redis.hgetall(RTables.HASH_DUEL_QUEUE(code))
                await self.redis.delete(RTables.HASH_DUEL_QUEUE(code))
                opponent_id = None
                for key, value in players.items():
                    decoded_key = key.decode()
                    if decoded_key != str(client.id):
                        opponent_id = decoded_key
                        break
                await asend_group(self.service_group, EventType.NOTIFICATION, ResponseAction.REFUSED_DUEL)
                await asend_group(RTables.GROUP_NOTIF(opponent_id),
                                  EventType.NOTIFICATION,
                                  ResponseAction.DUEL_REFUSED,
                                  {
                                      "username": await client.aget_profile_username()
                                  })

    async def _handle_get_opponent_name(self, data, client):
        opponent = data.get('data').get('args').get('opponent')
        if not opponent:
            return await asend_group_error(RTables.GROUP_NOTIF(client.id), ResponseError.OPPONENT_NOT_FOUND)
        return await asend_group(RTables.GROUP_NOTIF(client.id),
                                 EventType.NOTIFICATION,
                                 ResponseAction.GET_OPPONENT,
                                 {
                                     "opponent": opponent
                                 })

    async def get_opponent_username(self, duel_code, client_id):
        if not await self.redis.exists(RTables.HASH_DUEL_QUEUE(duel_code)):
            return None

        if await self.redis.hexists(RTables.HASH_DUEL_QUEUE(duel_code), str(client_id)) is False:
            return None

        players = await self.redis.hgetall(RTables.HASH_DUEL_QUEUE(duel_code))

        opponent_id = None
        for key, _ in players.items():
            decoded_key = key.decode()
            if decoded_key != str(client_id):
                opponent_id = decoded_key
                break

        if opponent_id is None:
            return None

        # Get opponent client object
        opponent = await Clients.aget_client_by_id(opponent_id)
        if opponent is None:
            return None

        # Return opponent's username
        return await opponent.aget_profile_username()

    # manage friends block and unblock
    async def _handle_block_unblock_friend(self, data, client):
        try:
            target = await Clients.aget_client_by_username(data.get('data').get('args').get('target_name'))
            if target is None:
                return await asend_group_error(self.service_group, ResponseError.USER_NOT_FOUND)
            friend_table = await client.get_friend_table()
            status = data.get('data').get('args').get('status')
            if status == "block":
                await friend_table.block_user(target)
                await asend_group(RTables.GROUP_CHAT(client.id),
                                  EventType.CHAT,
                                  ResponseAction.FRIEND_BLOCKED,
                                  {
                                      "message": "successfully block friend",
                                      "username": await target.aget_profile_username()
                                  })
            elif status == "unblock":
                await friend_table.unblock_user(target)
                await asend_group(self.service_group,
                                  EventType.NOTIFICATION,
                                  ResponseAction.FRIEND_UNBLOCKED,
                                  {
                                      "message": "successfully unblock friend",
                                      "username": await target.aget_profile_username()
                                  })
        except Exception as e:
            return await asend_group_error(self.service_group, ResponseError.INTERNAL_ERROR)

    async def _handle_ping(self, data, client):
        return await asend_group(self.service_group, EventType.NOTIFICATION, ResponseAction.PONG)

    async def _handle_check_online_status(self, data, client):
        target_username = data.get('data').get('args').get('target_name')
        target = await Clients.aget_client_by_username(target_username)  # async so async getter

        if target is None:
            return await asend_group_error(self.service_group, ResponseError.USER_NOT_FOUND)  # Sending back to the one who asked only

        # Check if the user has an active notification socket in Redis
        is_online = await self.redis.hget(
            name=RTables.HASH_CLIENT(target.id),
            key=str(EventType.NOTIFICATION.value)
        ) is not None

        # Send response only to the requesting client
        await asend_group(
            self.service_group,  # This sends only to the requesting client
            EventType.NOTIFICATION,
            ResponseAction.ACK_ONLINE_STATUS,  # You'll need to add this to your ResponseAction enum
            {
                # "user_id": str(target.id), #Do i really want to send back the id ?
                "username": target_username,
                "online": is_online
            }
        )

    async def _handle_tournament_invitation_response(self, data, client):
        code = data.get('data').get('args').get('tournament_code')
        if code is None:
            return await asend_group_error(self.service_group, ResponseError.JSON_ERROR)
        action = data.get('data').get('args').get('action')
        inviter_username = data.get('data').get('args').get('inviter_username')

        inviter = await Clients.aget_client_by_username(inviter_username)
        if inviter is None:
            return await asend_group_error(self.service_group, ResponseError.USER_NOT_FOUND)

        invitation_key = f"{RTables.HASH_TOURNAMENT_INVITATION}:{code}:{client.id}"
        if not await self.redis.exists(invitation_key):
            return await asend_group_error(self.service_group, ResponseError.INVITATION_NOT_FOUND)

        if not await self.redis.exists(RTables.HASH_TOURNAMENT_QUEUE(code)):
            await self.redis.delete(invitation_key)
            return await asend_group_error(self.service_group, ResponseError.TOURNAMENT_NOT_EXIST)

        if action == "accept":
            if await Clients.acheck_in_queue(client, self.redis):
                await self.redis.delete(invitation_key)
                return await asend_group_error(self.service_group, ResponseError.ALREADY_IN_QUEUE)

            await self.redis.hset(RTables.HASH_TOURNAMENT_QUEUE(code), str(client.id), 'True')

            channel_name = await self.redis.hget(name=RTables.HASH_CLIENT(client.id), key=str(EventType.TOURNAMENT.value))
            if channel_name:
                channel_name = channel_name.decode('utf-8')
                await self.channel_layer.group_add(RTables.GROUP_TOURNAMENT(code), channel_name)

            await asend_group(self.service_group, EventType.NOTIFICATION, ResponseAction.TOURNAMENT_INVITATION_ACCEPTED, {
                "tournament_code": code
            })

            await asend_group(RTables.GROUP_NOTIF(inviter.id), EventType.NOTIFICATION, ResponseAction.TOURNAMENT_INVITATION_ACCEPTED_BY, {
                "username": await client.aget_profile_username(),
                "tournament_code": code
            })
        else:
            await asend_group(self.service_group, EventType.NOTIFICATION, ResponseAction.TOURNAMENT_INVITATION_REJECTED, {
                "tournament_code": code
            })

            await asend_group(RTables.GROUP_NOTIF(inviter.id), EventType.NOTIFICATION, ResponseAction.TOURNAMENT_INVITATION_REJECTED_BY, {
                "username": await client.aget_profile_username(),
                "tournament_code": code
            })

        await self.redis.delete(invitation_key)

    async def disconnect(self, client):
        await super().disconnect(client)

        # Remove this client's notification service from Redis
        await self.redis.hdel(RTables.HASH_CLIENT(client.id), str(EventType.NOTIFICATION.value))

        username = await self.get_username(client)
        online_clients = await aget_all_online_clients(self.redis)

        # Notify other clients that this user is offline
        for client_key in online_clients:
            if client_key != f"client_{client.id}":
                await asend_group(
                    client_key,
                    EventType.NOTIFICATION,
                    ResponseAction.ACK_ONLINE_STATUS,
                    {
                        "username": username,
                        "online": False
                    }
                )
