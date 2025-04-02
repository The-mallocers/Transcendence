import logging

from django.forms import ValidationError
from apps.shared.models import Clients
from apps.notifications.models import Friend
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
        # target is the client that I want to add
        target = await Clients.ASget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await send_group_error(client.id, ResponseError.USER_NOT_FOUND)
        friendTargetTable = await target.get_friend_table()
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
        target = await Clients.ASget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await send_group_error(client.id, ResponseError.USER_NOT_FOUND)
        try:
            # add the pending friend
            friendTable = await client.get_friend_table()
            await friendTable.accept_pending_friend(target)
            # add the friend from the other person
            friendTable = await target.get_friend_table()
            await friendTable.accept_other_friend(client)
        except:
            return await send_group_error(client.id, ResponseError.USER_ALREADY_FRIEND_OR_NOT_PENDING_FRIEND)     
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
                                    "username": await client.aget_profile_username()
                                })
        
    async def _handle_refuse_friend_request(self, data, client):
        print(f"Refuse friend request and searching for username: '{data['data']['args']['target_name']}'")
        target = await Clients.ASget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await send_group_error(client.id, ResponseError.USER_NOT_FOUND)
        try:
            # refuse the pending friend request
            friendTable = await client.get_friend_table()
            await friendTable.refuse_pending_friend(target)

        except:
            return await send_group_error(client.id, ResponseError.USER_ALREADY_FRIEND_OR_NOT_PENDING_FRIEND, )        
        await send_group(client.id, EventType.NOTIFICATION, 
                                ResponseAction.ACK_REFUSE_FRIEND_REQUEST,
                                {
                                    "sender": str(target.id),
                                    "username": await target.aget_profile_username()
                                })
        
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
        except ValidationError:
            return await send_group_error(client.id, ResponseError.NOT_FRIEND)
        except Exception as e:
            print(f"Error in delete friend operation: {e}")
            return await send_group_error(client.id, ResponseError.INTERNAL_ERROR)
        
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
        
    
    async def handle_disconnect(self, client):
        pass
