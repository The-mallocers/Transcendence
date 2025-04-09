from redis.commands.json.path import Path

from apps.client.models import Clients
from utils.enums import GameStatus, ResponseError, status_order, RTables, PlayerSide
from utils.websockets.channel_send import asend_group_error
from utils.websockets.services.services import BaseServices


class GameService(BaseServices):
    async def init(self, client: Clients) -> bool:
        await super().init()
        game_id_bytes = await self.redis.hget(name=RTables.HASH_MATCHES, key=str(client.id))
        game_id = game_id_bytes.decode('utf-8')

        if game_id:
            self.game_key = RTables.JSON_GAME(game_id)
            self.pL = await self.redis.json().get(self.game_key, Path(PlayerSide.LEFT))
            self.pR = await self.redis.json().get(self.game_key, Path(PlayerSide.RIGHT))
            return True
        else:
            await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.NO_GAME)
            self._logger.error(f"No active game found for client {client.id}")
        return True

    # async def process_action(self, data: Dict[str, Any], *args):
    #     # if await self.redis.hget(name='player_game', key=str(args[0].id)) is None:
    #     #     client = await Clients.get_client_by_player_id_async(args[0].id)
    #     #     await send_group_error(RTable.GROUP_CLIENT(client.id, ResponseError.NO_GAME)
    #     # else:
    #     return await super().process_action(data, *args)

    async def _handle_start_game(self, data, client: Clients):
        status = GameStatus(await self.redis.json().get(self.game_key, Path('status')))
        if status_order.index(status) < status_order.index(GameStatus.STARTING):
            await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.NOT_READY_TO_START)
        elif status_order.index(status) > status_order.index(GameStatus.STARTING):
            await asend_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.ALREADY_START)
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

    async def handle_disconnect(self, client):
        await self.redis.json().set(self.game_key, Path('status'), GameStatus.ENDING)
