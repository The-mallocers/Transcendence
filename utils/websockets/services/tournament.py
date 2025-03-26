from utils.websockets.services.services import BaseServices


class TournamentService(BaseServices):
    async def init(self, *args) -> bool:
        pass

    async def _handle_create_tournament(self, data, player):
        pass

    async def _handle_join_tournament(self, data, player):
        pass

    async def _handle_leave_tournament(self, data, player):
        pass

    async def _handle_list_tournament(self, data, player):
        pass

    async def _handle_start_tournament(self, data, player):
        pass

    async def handle_disconnect(self, client):
        pass
