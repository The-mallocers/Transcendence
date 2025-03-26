
from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseAction, ResponseError
from utils.websockets.channel_send import send_group, send_group_error
from utils.websockets.services.services import BaseServices


class NotificationService(BaseServices):
    async def init(self, client):
        await super().init()
    
    async def _handle_send_friend_request(self, data, client):
        print(f"Searching for username: '{data['data']['args']['target_name']}'")
        target = await Clients.ASget_client_by_username(data['data']['args']['target_name'])
        if target is None:
            return await send_group_error(client.id, ResponseError.USER_NOT_FOUND)
        
        await send_group(target.id, EventType.NOTIFICATION, ResponseAction.NOTIF_TEST, {"message": "hello veux tu etre mon ami ??????????????", "sender": str(client.id)})
        
        # await send_group(client.id, EventType.NOTIFICATION, ResponseAction.NOTIF_TEST)
    
    async def handle_disconnect(self, client):
        pass
