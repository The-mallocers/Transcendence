from typing import Dict, Any

from apps.game.manager import GameManager
from apps.player.manager import PlayerManager
from apps.player.models import Player
from apps.shared.models import Clients
from utils.pong.enums import GameStatus, ResponseError, status_order
from utils.websockets.channel_send import send_group_error
from utils.websockets.services.services import BaseServices


class GameService(BaseServices):
    def __init__(self):
        super().__init__()
        self.game_manager: GameManager = None

    async def init(self, player: Player):
        await super().init()
        game_id_bytes = await self.redis.hget(name="player_game", key=str(player.id))

        if game_id_bytes:
            game = await GameManager.get_game_db_async(game_id_bytes.decode('utf-8'))
            self.game_manager = GameManager(game, self.redis)
            self.game_manager._redis = self.redis
            self.game_manager.pL = PlayerManager(await self.game_manager.rget_pL_id(), self.game_manager.get_id(),
                                                 self.redis)
            self.game_manager.pR = PlayerManager(await self.game_manager.rget_pR_id(), self.game_manager.get_id(),
                                                 self.redis)
            await self.game_manager.pL.paddle.update()
            await self.game_manager.pR.paddle.update()
        else:
            client = await Clients.get_client_by_player_id_async(player.id)
            await send_group_error(client.id, ResponseError.NO_GAME)
            self._logger.error(f"No active game found for player {player.id}")
        return True

    async def process_action(self, data: Dict[str, Any], *args):
        # if await self.redis.hget(name='player_game', key=str(args[0].id)) is None:
        #     client = await Clients.get_client_by_player_id_async(args[0].id)
        #     await send_group_error(client.id, ResponseError.NO_GAME)
        # else:
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
        if await self.game_manager.rget_status() is GameStatus.RUNNING:
            if str(player.id) == str(self.game_manager.pL.id):
                await self.game_manager.pL.paddle.set_move(data['data']['args'])
            if str(player.id) == str(self.game_manager.pR.id):
                await self.game_manager.pR.paddle.set_move(data['data']['args'])

    async def handle_disconnect(self, client):
        p1_id = await self.game_manager.rget_pL_id()
        p2_id = await self.game_manager.rget_pR_id()
        opponent_id = p1_id if client.id is not p1_id else p2_id
        opponent_client: Clients = await Clients.get_client_by_player_id_async(opponent_id)
        # il faut checker quand un player se deco alors que la game est en starting et donc pas commencer
        if opponent_client:
            await send_group_error(opponent_id, ResponseError.OPPONENT_LEFT, close=True)
            await self.game_manager.rset_status(GameStatus.ENDING)


        #Le code si dessous a pour but de checker si un joueur se deconnecte pendant une game
        #On veut register ca comme une defaite pour lui
        #Je ne sais pas vraiment comment check si la deco arrive dans une des autres phases d'une game

        
        #Alexandre a l'aide
        # await self.game_manager.update_disconnect_result(client, opponent_client)

