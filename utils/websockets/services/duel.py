from utils.websockets.services.services import BaseServices


class DuelService(BaseServices):
    async def init(self, *args) -> bool:
        pass

    async def _handle_create_duel(self, data, player):
        pass

    async def _handle_join_duel(self, data, player):
        pass

    async def _handle_leave_duel(self, data, player):
        pass

    async def _handle_list_duel(self, data, player):
        pass

    async def _handle_start_duel(self, data, player):
        pass

    async def handle_disconnect(self, client):
        pass
