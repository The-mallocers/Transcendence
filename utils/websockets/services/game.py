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
        # print("in paddle move")
        status = GameStatus(await self.redis.json().get(self.game_key, Path('status')))
        is_local = await self.redis.json().get(self.game_key, Path('local'))
        if status is GameStatus.RUNNING:
            # print("Game is running")
            if is_local is True:
                # print('game is local')
                # print(f'data is ', data['data']['args']['side'])
                # print("printing the weird player side thing")
                # print(PlayerSide(data['data']['args']['side']))
                if PlayerSide(data['data']['args']['side']) == PlayerSide.LEFT:
                    print("move is left")
                    await self.redis.json().set(self.game_key, Path('player_left.paddle.move'), data['data']['args']['move'])
                if PlayerSide(data['data']['args']['side']) == PlayerSide.RIGHT:                    
                    print("move is right")
                    await self.redis.json().set(self.game_key, Path('player_right.paddle.move'), data['data']['args']['move'])
            else:
                if str(client.id) == self.pL['id']:
                    await self.redis.json().set(self.game_key, Path('player_left.paddle.move'), data['data']['args']['move'])
                if str(client.id) == self.pR['id']:
                    await self.redis.json().set(self.game_key, Path('player_right.paddle.move'), data['data']['args']['move'])

    async def disconnect(self, client):
        pass
