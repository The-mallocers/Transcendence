from redis.commands.json.path import Path

from apps.client.models import Clients
from utils.enums import GameStatus, ResponseError, game_status_order, RTables, PlayerSide, EventType
from utils.websockets.channel_send import asend_group_error
from utils.websockets.services.services import BaseServices


class GameService(BaseServices):
    async def init(self, client: Clients, *args) -> bool:
        await super().init(client)
        self.service_group = f'{EventType.GAME.value}_{client.id}'
        game_id_bytes = await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id))

        if game_id_bytes:
            game_id = game_id_bytes.decode('utf-8')
            self.game_key = RTables.JSON_GAME(game_id)
            self.pL = await self.redis.json().get(self.game_key, Path(PlayerSide.LEFT))
            self.pR = await self.redis.json().get(self.game_key, Path(PlayerSide.RIGHT))
            return True
        else:
            await asend_group_error(self.service_group, ResponseError.NO_GAME)
            self._logger.error(f"No active game found for client {client.id}")
        return True

    async def _handle_start_game(self, data, client: Clients):
        status = GameStatus(await self.redis.json().get(self.game_key, Path('status')))
        if game_status_order.index(status) < game_status_order.index(GameStatus.STARTING):
            await asend_group_error(self.service_group, ResponseError.NOT_READY_TO_START)
        elif game_status_order.index(status) > game_status_order.index(GameStatus.STARTING):
            await asend_group_error(self.service_group, ResponseError.ALREADY_START)
        elif status is GameStatus.STARTING:
            await self.redis.json().set(self.game_key, Path('status'), GameStatus.STARTING)

    async def _handle_stop_game(self, data, client: Clients):
        # await self.game_manager.rset_status(GameStatus.ENDING)
        pass

    async def _handle_paddle_move(self, data, client: Clients):
        status = GameStatus(await self.redis.json().get(self.game_key, Path('status')))
        if status is GameStatus.RUNNING:
            if str(client.id) == self.pL['id']:
                await self.redis.json().set(self.game_key, Path('player_left.paddle.move'), data['data']['args'])
            if str(client.id) == self.pR['id']:
                await self.redis.json().set(self.game_key, Path('player_right.paddle.move'), data['data']['args'])

    async def disconnect(self, client):
        if self.game_key:
            await self.redis.json().set(self.game_key, Path('status'), GameStatus.ENDING)
