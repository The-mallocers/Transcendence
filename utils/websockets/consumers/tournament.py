from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.tournament import TournamentService


class TournamentConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = TournamentService()

    async def connect(self):
        return await super().connect()

    async def disconnect(self, close_code):
        return await super().disconnect(close_code)

    async def receive(self, text_data=None, bytes_data=None):
        return await super().receive(text_data, bytes_data)
