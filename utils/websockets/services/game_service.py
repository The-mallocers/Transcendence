from typing import Dict, Any

from apps.game.manager import GameManager
from apps.player.models import Player
from apps.shared.models import Clients
from utils.pong.enums import GameStatus, ResponseError, status_order
from utils.websockets.channel_send import send_group_error
from utils.websockets.services.services import BaseServices


class GameService(BaseServices):
    def __init__(self):
        super().__init__()
        self.game_manager = GameManager()

    async def init(self, player: Player):
        game_id_bytes = await self._redis.hget(name="player_game", key=str(player.id))

        if game_id_bytes:
            game_id = game_id_bytes.decode('utf-8')

            self.game_manager = GameManager()
            await self.game_manager.load_by_id(game_id)
        else:
            client = await Clients.get_client_by_player_id_async(player.id)
            await send_group_error(client.id, ResponseError.NO_GAME)
            self._logger.error(f"No active game found for player {player.id}")

    async def process_action(self, data: Dict[str, Any], *args):
        if await self._redis.hget(name='player_game', key=str(args[0].id)) is None:
            client = await Clients.get_client_by_player_id_async(args[0].id)
            await send_group_error(client.id, ResponseError.NO_GAME)
        else:
            return await super().process_action(data, *args)

    async def _handle_start_game(self, data, player: Player):
        status = await self.game_manager.rget_status()
        if status_order.index(status) < status_order.index(GameStatus.STARTING):
            await send_group_error(player.id, ResponseError.NOT_READY_TO_START)
        elif status_order.index(status) > status_order.index(GameStatus.STARTING):
            await send_group_error(player.id, ResponseError.ALREADY_START)
        elif status is GameStatus.STARTING:
            await self.game_manager.rset_status(GameStatus.RUNNING)

    async def _handle_stop_game(self, data, player: Player):
        await self.game_manager.rset_status(GameStatus.ENDING)

    async def _handle_paddle_move(self, data, player: Player):
        if str(player.id) == str(self.game_manager.pL.id):
            if data['data']['args'] == 'up':
                await self.game_manager.pL.paddle.increase_y()
            if data['data']['args'] == 'down':
                await self.game_manager.pL.paddle.decrease_y()
        if str(player.id) == str(self.game_manager.pR.id):
            if data['data']['args'] == 'up':
                await self.game_manager.pR.paddle.increase_y()
            if data['data']['args'] == 'down':
                await self.game_manager.pR.paddle.decrease_y()

    async def handle_disconnect(self, client):
        p1_id = await self.game_manager.rget_pL_id()
        p2_id = await self.game_manager.rget_pR_id()
        opponent_id = p1_id if client.id is not p1_id else p2_id
        opponent_client: Clients = await Clients.get_client_by_player_id_async(opponent_id)
        # il faut checker quand un player se deco alors que la game est en starting et donc pas commencer
        if opponent_client:
            await send_group_error(opponent_id, ResponseError.OPPONENT_LEFT, close=True)
            await self.game_manager.rset_status(GameStatus.ENDING)
