import logging
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
                
        await send_group(client.id, 
                                EventType.NOTIFICATION, 
                                ResponseAction.ACK_SEND_FRIEND_REQUEST, 
                                {"message": "hello veux tu etre mon ami ??????????????", 
                                 "sender": str(client.id)})
        
    # client is the client that want to add the friend from his pending list
    # target is the friend pending
    async def _handle_accept_friend_request(self, data, client):
        print(f"Accept friend and searching for username: '{data['data']['args']['target_id']}'")
        target_id = data['data']['args']['target_id']
        target = await Clients.ASget_client_by_ID(target_id)
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
                         ResponseAction.NOTIF_TEST, 
                         {"message": "hello oui je veux etre ton ami !!!!!!!!", 
                          "sender": str(client.id)})
    
    async def handle_disconnect(self, client):
        pass
