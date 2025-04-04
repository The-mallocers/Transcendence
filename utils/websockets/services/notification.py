import logging
from apps import notifications

from django.forms import ValidationError
from apps.shared.models import Clients
from apps.chat.models import Rooms, Messages
from apps.notifications.admin import check_client_exists
# from apps.notifications.models import Friend
from utils.pong.enums import EventType, ResponseAction, ResponseError
from utils.websockets.channel_send import send_group, send_group_error
from utils.websockets.services.services import BaseServices


class NotificationService(BaseServices):
    async def init(self, client):
        await super().init()
    
    # Client is the person that want to add a friend to his friend list
    # Target is the friends to add
    # When i add a friend I put the client is to pending friend of the target person
    async def _handle_send_friend_request(self, data, client):
        print(f"Searching for username: '{data['data']['args']['target_name']}'")
        print("the person that ask the friendship ", client.id)
        # target is the client that I want to add
        target = await Clients.ASget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await send_group_error(client.id, ResponseError.USER_NOT_FOUND)
        friendTargetTable = await target.get_friend_table()
        
        #check if the friend ask is already in my pending list
        username = await client.Aget_pending_request_by_client(target)
        # if the username exist in my pending list I accept it
        if username is not None:
            friend_request_data = {
                "event": "notification",
                "data": {
                    "action" : "accept_friend_request",
                    "args": {
                        "target_name": data['data']['args']['target_name']
                    }
                }
            }
            return await self._handle_accept_friend_request(friend_request_data, client)       
        
        askfriend = await friendTargetTable.add_pending_friend(client)
        # if I am already his friend 
        if askfriend is None:
            return await send_group_error(client.id, ResponseError.USER_ALREADY_MY_FRIEND)
        await send_group(target.id, 
                                EventType.NOTIFICATION, 
                                ResponseAction.ACK_SEND_FRIEND_REQUEST,
                                {
                                    "sender": str(client.id),
                                    "username": await client.aget_profile_username()
                                })
    
        
    # client is the client that want to add the friend from his pending list
    # target is the friend pending
    async def _handle_accept_friend_request(self, data, client):
        print(f"Accept friend and searching for username: '{data['data']['args']['target_name']}'")
        print("the person that ask the friendship ", client.id)
        target = await Clients.ASget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await send_group_error(client.id, ResponseError.USER_NOT_FOUND)
        try:
            # add the pending friend
            friendTable = await client.get_friend_table()
            await friendTable.accept_pending_friend(target)
            print("accepting pending friend")
            # add the friend from the other person
            friendTable = await target.get_friend_table()
            await friendTable.accept_other_friend(client)
            print("accept friend")
            # Create Room
            room = await Rooms.create_room()
            room.admin = client
            await room.asave()
            await room.add_client(client)
            await room.add_client(target)
            
            print("created the new room")
            #return all rooms to the target to update his messages rooms
            # all_rooms = Rooms.get_room_by_client_id(target)
            # print("all rooms: ", all_rooms)
            # await send_group(target.id, EventType.CHAT, 
            #             ResponseAction.ALL_ROOM_RECEIVED,
            #             {"rooms": all_rooms})
            
            await send_group(client.id, EventType.NOTIFICATION, 
                                    ResponseAction.ACK_ACCEPT_FRIEND_REQUEST_HOST,
                                    {
                                        "sender": str(target.id),
                                        "username": await target.aget_profile_username()
                                    })
            
            await send_group(target.id, EventType.NOTIFICATION, 
                                    ResponseAction.ACK_ACCEPT_FRIEND_REQUEST,
                                    {
                                        "sender": str(client.id),
                                        "username": await client.aget_profile_username(),
                                        "room": str(room.id)
                                    })
            
        except:
            return await send_group_error(client.id, ResponseError.USER_ALREADY_FRIEND_OR_NOT_PENDING_FRIEND)     

        
    async def _handle_refuse_friend_request(self, data, client):
        print(f"Refuse friend request and searching for username: '{data['data']['args']['target_name']}'")
        target = await Clients.ASget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await send_group_error(client.id, ResponseError.USER_NOT_FOUND)
        try:
            # refuse the pending friend request
            friendTable = await client.get_friend_table()
            await friendTable.refuse_pending_friend(target)
            await send_group(client.id, EventType.NOTIFICATION, 
                                    ResponseAction.ACK_REFUSE_FRIEND_REQUEST,
                                    {
                                        "sender": str(target.id),
                                        "username": await target.aget_profile_username()
                                    })
        except:
            return await send_group_error(client.id, ResponseError.USER_ALREADY_FRIEND_OR_NOT_PENDING_FRIEND, )        
        
    async def _handle_delete_friend(self, data, client):
        print(f"Deleting friend and searching for username: '{data['data']['args']['target_name']}'")
        target = await Clients.ASget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await send_group_error(client.id, ResponseError.USER_NOT_FOUND)
        
        try:
            client_friend_table = await client.get_friend_table()
            await client_friend_table.remove_friend(target)
            
            target_friend_table = await target.get_friend_table()
            await target_friend_table.remove_friend(client)
            await send_group(client.id, 
                            EventType.NOTIFICATION, 
                            ResponseAction.ACK_DELETE_FRIEND,
                            {
                                "sender": str(target.id),
                                "username": await target.aget_profile_username()
                            })
            
            await send_group(target.id, 
                            EventType.NOTIFICATION, 
                            ResponseAction.ACK_FRIEND_DELETED_HOST,
                            {
                                "sender": str(client.id),
                                "username": await client.aget_profile_username()
                            })
            #get the room to delete
            room = await Rooms.Aget_room_by_client_id(client.id)
            print(room)
            if room is None:
                return
            # First delete all messages corresponding to the two users
            await Messages.Adelete_all_messages_by_room_id(room)
            # Then delete the two user from the room
            await Rooms.Adelete_all_user_by_room_id(room)
            # Then delete the room
            await room.Adelete_room()
        except ValidationError:
            return await send_group_error(client.id, ResponseError.NOT_FRIEND)
        except Exception as e:
            print(f"Error in delete friend operation: {e}")
            return await send_group_error(client.id, ResponseError.INTERNAL_ERROR)
        
    async def handle_disconnect(self, client):
        pass
