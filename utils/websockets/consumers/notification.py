from channels.db import database_sync_to_async

from utils.enums import EventType, ResponseAction
from utils.websockets.channel_send import asend_group
from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.notification import NotificationService


class NotificationfConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = NotificationService()

    # Sending the signal to all connected user that I am connecting
    async def connect(self):
        await super().connect()
        username = await self.get_username()
        online_clients = await self.get_all_online_clients()
        for client in online_clients:
            await asend_group(
                client,
                EventType.NOTIFICATION,
                ResponseAction.ACK_ONLINE_STATUS,
                {
                    "username": username,
                    "online": True
                }
            )
        return True

    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        username = await self.get_username()
        online_clients = await self.get_all_online_clients()
        for client in online_clients:
            await asend_group(
                client,
                EventType.NOTIFICATION,
                ResponseAction.ACK_ONLINE_STATUS,
                {
                    "username": username,
                    "online": False
                }
            )
        return True

    @database_sync_to_async
    def get_username(self):
        return self.client.profile.username
