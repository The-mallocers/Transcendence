import asyncio
import logging
import pickle
from typing import Dict

from redis.commands.json.path import Path

from apps.game.manager import GameManager
from apps.player.manager import PlayerManager
from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer
from apps.pong.utils import GameState
from utils.pong.base_class import BaseServices
from utils.pong.enums import RequestAction, ResponseError, EventType, \
    ResponseAction, GameStatus
from utils.sender import send_player, send_game


class MatchmakingService(BaseServices):
    async def init(self, **kwargs):
        pass

    async def _handle_join_queue(self, data: Dict, player: Player):
        await self._redis.hset(name="matchmaking_queue", key=str(player.id), value=player.stats.mmr)
        await send_player(player.id, EventType.MATCHMAKING, ResponseAction.JOIN_QUEUE)

    async def _handle_leave_queue(self, data: Dict, player: Player):
        await self._redis.hdel("matchmaking_queue", str(player.id))
        await send_player(player.id, EventType.MATCHMAKING, ResponseAction.LEFT_QUEUE)


class GameService(BaseServices):
    def __init__(self):
        super().__init__()
        self.game_manager = GameManager()
        self.player1_manager = PlayerManager()
        self.player2_manager = PlayerManager()

    async def init(self, player_id):
        game_id_bytes = await self._redis.get(f"active_game:{player_id}")

        if game_id_bytes:
            game_id = game_id_bytes.decode('utf-8')

            self.game_manager = GameManager()
            await self.game_manager.load_by_id(game_id)
        else:
            self._logger.error(f"No active game found for player {player_id}")

    async def _handle_start_game(self, data: Dict, game: GameState, player: Player):
        await self.game_manager.set_status(GameStatus.RUNNING)
        await send_game(await self.game_manager.get_id(), EventType.GAME, ResponseAction.LEFT_QUEUE)



    async def _handle_paddle_move(self, data: Dict, game: GameState, player: Player):
        if player == game.player_1 or player == game.player_2:
            await player.move(data.get('direction'))
            return {
                'type': RequestAction.PADDLE_MOVE,
                'player_id': player.id,
                'paddle': PaddleSerializer(player.paddle).data
            }
        else:
            return {
                'error': ResponseError.NOT_IN_GAME,
                'player_id': str(player.id)
            }

    async def _handle_is_ready(self, data: Dict, game: GameState, player: Player):
        if player == game.player_1 or player == game.player_2:
            player.is_ready = True
            return {
                'type': RequestAction.IS_READY,
                'player_id': player.id,
                'is_ready': player.is_ready
            }

    async def handle_disconnect(self, room: str, player_id: str):
        if room in self.game_states and player_id in \
                self.game_states[room]['players']:
            self.game_states[room]['players'][player_id].is_active = False

