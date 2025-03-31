from redis.commands.json.path import Path

from apps.client.models import Clients
from utils.enums import GameStatus, ResponseError, status_order
from utils.websockets.channel_send import asend_group_error
from utils.websockets.services.services import BaseServices


class GameService(BaseServices):
    def __init__(self):
        super().__init__()
        # self.game_manager: GameManager = None

    async def init(self, client: Clients) -> bool:
        await super().init()
        game_id_bytes = await self.redis.hget(name="current_matches", key=str(client.id))
        game_id = game_id_bytes.decode('utf-8')

        if game_id:
            self.game_key = f'game:{game_id}'
            self.pL = await self.redis.json().get(self.game_key, Path('player_left'))
            self.pR = await self.redis.json().get(self.game_key, Path('player_right'))
            return True
        else:
            await asend_group_error(client.id, ResponseError.NO_GAME)
            self._logger.error(f"No active game found for client {client.id}")
        return True

    # async def process_action(self, data: Dict[str, Any], *args):
    #     # if await self.redis.hget(name='player_game', key=str(args[0].id)) is None:
    #     #     client = await Clients.get_client_by_player_id_async(args[0].id)
    #     #     await send_group_error(client.id, ResponseError.NO_GAME)
    #     # else:
    #     return await super().process_action(data, *args)

    async def _handle_start_game(self, data, client: Clients):
        status = GameStatus(await self.redis.json().get(self.game_key, Path('status')))
        if status_order.index(status) < status_order.index(GameStatus.STARTING):
            await asend_group_error(client.id, ResponseError.NOT_READY_TO_START)
        elif status_order.index(status) > status_order.index(GameStatus.STARTING):
            await asend_group_error(client.id, ResponseError.ALREADY_START)
        elif status is GameStatus.STARTING:
            await self.redis.json().set(self.game_key, Path('status'), GameStatus.STARTING)

    async def _handle_stop_game(self, data, client: Clients):
        await self.game_manager.rset_status(GameStatus.ENDING)

    async def _handle_paddle_move(self, data, client: Clients):
        status = GameStatus(await self.redis.json().get(self.game_key, Path('status')))
        if status is GameStatus.RUNNING:
            if str(client.id) == self.pL['id']:
                await self.redis.json().set(self.game_key, Path('player_left.paddle.move'), data['data']['args'])
            if str(client.id) == self.pR['id']:
                await self.redis.json().set(self.game_key, Path('player_right.paddle.move'), data['data']['args'])

    async def handle_disconnect(self, client):
        self._logger.info('disconnect')
        await self.redis.json().set(self.game_key, Path('status'), GameStatus.ENDING)

        # Envoyer un message a celui qui s'est pas deconnecter qu'il a gagner (pour que le front le redirige)
        # On veux arreter la game thread et faire en sorte qu'il comprenne que c'est une deco
        # Update le score specialement pour une disconnect

        # Be careful, this breaks because it sets stuff back to ending instead of finished.

        # p1_id = await self.game_manager.rget_pL_id()
        # p2_id = await self.game_manager.rget_pR_id()
        # opponent_id = p1_id if client.id is not p1_id else p2_id
        # opponent_client: Clients = await Clients.get_client_by_player_id_async(opponent_id)
        # # il faut checker quand un player se deco alors que la game est en starting et donc pas commencer
        # if opponent_client:
        #     await send_group_error(opponent_id, ResponseError.OPPONENT_LEFT, close=True)
        #     await self.game_manager.rset_status(GameStatus.ENDING)

        # Le code si dessous a pour but de checker si un joueur se deconnecte pendant une game
        # On veut register ca comme une defaite pour lui
        # Je ne sais pas vraiment comment check si la deco arrive dans une des autres phases d'une game

        # Alexandre a l'aide
        # await self.game_manager.update_disconnect_result(client, opponent_client)
