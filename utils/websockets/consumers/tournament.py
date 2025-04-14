from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.tournament import TournamentService


class TournamentConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = TournamentService()
