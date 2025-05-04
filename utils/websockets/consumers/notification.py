from utils.enums import EventType, ResponseAction
from utils.websockets.channel_send import asend_group
from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.notification import NotificationService


class NotificationfConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = NotificationService()
        
#Be very careful with implementing this for some reason ?
#@database_sync_to_async we might need this !
    async def connect(self):
        await super().connect()
        # username = self.client.profile.username # This is no bueno without
        #Since the way a notification group is like this:
        # self.service_group = f'{EventType.NOTIFICATION.value}_{client.id}'
        
        #First do a query to get all the 
        # # await asend_group(
        # #     self.service_group,
        # #     EventType.NOTIFICATION,
        # #     ResponseAction.ACK_ONLINE_STATUS,
        # #     {
        # #         "username": username,
        # #         "online": True
        # #     }
        # # )
        # return True

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
