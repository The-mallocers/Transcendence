from utils.enums import EventType, ResponseAction
from utils.websockets.channel_send import asend_group
from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.notification import NotificationService
from channels.db import database_sync_to_async


class NotificationfConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = NotificationService()
        
    #Sending the signal to all connected user that I am connecting
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
        username = self.client.profile.username
        await asend_group(
            self.service_group,
            EventType.NOTIFICATION,
            ResponseAction.ACK_ONLINE_STATUS,
            {
                "username": username,
                "online": False
            }
        )
    
    @database_sync_to_async
    def get_username(self):
        return self.client.profile.username
    
    async def get_all_online_clients(self):
        client_keys = await self._redis.keys("client_*")
        #Decode because this gets us the results in bytes
        if client_keys and isinstance(client_keys[0], bytes):
            client_keys = [key.decode() for key in client_keys]
        return client_keys