from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.notification import NotificationService


class NotificationfConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = NotificationService()
