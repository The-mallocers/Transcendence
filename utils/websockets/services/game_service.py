from typing import Dict

from apps.game.manager import GameManager
from apps.player.models import Player
from apps.pong.utils import GameState
from apps.shared.models import Clients
from utils.pong.enums import GameStatus, RequestAction
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
            self._logger.error(f"No active game found for player {player.id}")

    async def _handle_start_game(self, data, player: Player):
        await self.game_manager.rset_status(GameStatus.RUNNING)

    async def _handle_stop_game(self, data, player: Player):
        await self.game_manager.rset_status(GameStatus.ENDING)

    async def _handle_paddle_move(self, data, player: Player):
        await self.game_manager.p1.paddle.increase_y()
        # if player == game.player_1 or player == game.player_2:
        #     await player.move(data.get('direction'))
        #     return {
        #         'type': RequestAction.PADDLE_MOVE,
        #         'player_id': player.id,
        #         'paddle': PaddleSerializer(player.paddle).data
        #     }
        # else:
        #     return {
        #         'error': ResponseError.NOT_IN_GAME,
        #         'player_id': str(player.id)
        #     }

    async def _handle_is_ready(self, data: Dict, game: GameState, player: Player):
        if player == game.player_1 or player == game.player_2:
            player.is_ready = True
            return {
                'type': RequestAction.IS_READY,
                'player_id': player.id,
                'is_ready': player.is_ready
            }

    async def _handle_disconnect(self):
        pass
        # if room in self.game_states and player_id in \
        #         self.game_states[room]['players']:
        #     self.game_states[room]['players'][player_id].is_active = False