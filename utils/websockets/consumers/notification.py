from utils.enums import EventType, ResponseAction
from utils.websockets.channel_send import asend_group
from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.notification import NotificationService


class NotificationfConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = NotificationService()
        
    # async def connect(self):
    #     super().connect()
    #     username = self.client.profile.username
    #     await asend_group(
    #         self.service_group,
    #         EventType.NOTIFICATION,
    #         ResponseAction.ACK_ONLINE_STATUS,
    #         {
    #             "username": username,
    #             "online": True
    #         }
    #     )

    # async def disconnect(self):
    #     super().connect()
    #     username = self.client.profile.username
    #     await asend_group(
    #         self.service_group,
    #         EventType.NOTIFICATION,
    #         ResponseAction.ACK_ONLINE_STATUS,
    #         {
    #             "username": username,
    #             "online": True
    #         }
    #     )
