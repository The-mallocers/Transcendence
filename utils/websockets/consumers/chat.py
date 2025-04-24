from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.chat import ChatService


class ChatConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ChatService()

