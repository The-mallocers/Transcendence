from redis.commands.json.path import Path

from apps.client.models import Clients
from utils.enums import GameStatus, ResponseError, game_status_order, RTables, PlayerSide, EventType
from utils.websockets.channel_send import asend_group_error
from utils.websockets.services.services import BaseServices


VALID_SIDES = frozenset(['left', 'right'])
VALID_MOVES = frozenset(['idle', 'up', 'down'])

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
        validated = self.validate_move(data)
        if not validated:
            return
        
        side, move = validated

        status = GameStatus(await self.redis.json().get(self.game_key, Path('status')))
        is_local = await self.redis.json().get(self.game_key, Path('local'))
        if status is GameStatus.RUNNING:
            if is_local is True:
                if side == "left":
                    await self.redis.json().set(self.game_key, Path('player_left.paddle.move'), move) 
                elif side == "right": #PlayerSide.RIGHT.value
                    await self.redis.json().set(self.game_key, Path('player_right.paddle.move'), move)
            else:
                if str(client.id) == self.pL['id']:
                    await self.redis.json().set(self.game_key, Path('player_left.paddle.move'), move)
                if str(client.id) == self.pR['id']:
                    await self.redis.json().set(self.game_key, Path('player_right.paddle.move'), move)

    def validate_move(self, data):
        try:
            args = data['data']['args']
            side = args['side']
            move = args['move']
            
            # Fast membership tests using pre-computed sets
            if side in VALID_SIDES and move in VALID_MOVES:
                return side, move
                
        except (KeyError, TypeError):
            return None
        
        return None

    async def disconnect(self, client):
        pass
