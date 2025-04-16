from utils.enums import EventType
from utils.websockets.services.services import BaseServices


class TournamentService(BaseServices):
    async def init(self, client, *args) -> bool:
        self.service_group = f'{EventType.TOURNAMENT.value}_{client.id}'
        return await super().init(client)

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

    async def disconnect(self, client):
        pass
