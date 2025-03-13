from apps.game.manager import GameManager
from apps.player.models import Player
from apps.shared.models import Clients
from utils.pong.enums import GameStatus, ResponseError
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
            self._logger.error(f"No active game found for player {player.id}")

    async def _handle_start_game(self, data, player: Player):
        await self.game_manager.rset_status(GameStatus.RUNNING)

    async def _handle_stop_game(self, data, player: Player):
        await self.game_manager.rset_status(GameStatus.ENDING)

    async def _handle_paddle_move(self, data, player: Player):
        if str(player.id) == str(self.game_manager.p1.id):
            if data['data']['args'] == 'up':
                await self.game_manager.p1.paddle.increase_y()
            if data['data']['args'] == 'down':
                await self.game_manager.p1.paddle.decrease_y()
        if str(player.id) == str(self.game_manager.p2.id):
            if data['data']['args'] == 'up':
                await self.game_manager.p2.paddle.increase_y()
            if data['data']['args'] == 'down':
                await self.game_manager.p2.paddle.decrease_y()

    async def handle_disconnect(self, client):
        p1_id = await self.game_manager.rget_player1_id()
        p2_id = await self.game_manager.rget_player2_id()
        opponent_id = p1_id if client.id is not p1_id else p2_id
        opponent_client: Clients = await Clients.get_client_by_player_id_async(opponent_id)
        if opponent_client:
            await send_group_error(opponent_id, ResponseError.OPPONENT_LEAVE, close=True)
            await self.game_manager.rset_status(GameStatus.ENDING)
