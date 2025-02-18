import asyncio
import logging
from typing import Dict

from apps.game.manager import GameManager
from apps.player.manager import PlayerManager
from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer
from apps.pong.utils import GameState
from utils.pong.base_class import BaseServices
from utils.pong.enums import RequestAction, ErrorType, SendType


class MatchmakingService(BaseServices):
    async def _handle_join_matchmaking(self, data: Dict, player: Player):
        await self.redis_client.hset(name="matchmaking_queue", key=str(player.id), value=player.stats.mmr)
        await self.send_to_group(SendType.MATCHMAKING, 'join queue')

    async def _handle_leave_matchmaking(self, data: Dict, player: Player):
        await self.redis_client.hdel("matchmaking_queue", str(player.id))
        await self.send_to_group(SendType.MATCHMAKING, 'left queue')


class GameService(BaseServices):
    def __init__(self):
        super().__init__()
        self.game_manager = GameManager()
        self.player1_manager = PlayerManager()
        self.player2_manager = PlayerManager()

    async def _handle_join_game(self, data: Dict, game: GameState, player: Player):
        #Check if the player is arleady join
        if player == game.player_1 or player == game.player_2:
            return {
                'error': ErrorType.ALREADY_JOIN,
                'player_id': str(player.id)
            }
        else: #il faudra implementer le random pour savoir sur quel cote le joueur joue
            if game.player_1 is None:
                player.position = 'right'
                game.player_1 = player
            elif game.player_2 is None:
                player.position = 'left'
                game.player_2 = player
            else:
                return {
                    'error': ErrorType.GAME_FULL,
                    'player_id': str(player.id)
                }
            await player.async_save()

        return {
            'type': RequestAction.JOIN_GAME,
            'player_id': str(player.id)
        }

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
                'error': ErrorType.NOT_IN_GAME,
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

    async def _handle_start_game(self, data: Dict, game: GameState, player: Player):
        if game.player_1.is_ready and game.player_2.is_ready:
            game.active = True
            game.task = asyncio.create_task(self._game_task(game))
            return {
                'type': RequestAction.START_GAME,
            }
        else:
            return {
                'error': ErrorType.NOT_READY
            }

    async def handle_disconnect(self, room: str, player_id: str):
        if room in self.game_states and player_id in \
                self.game_states[room]['players']:
            self.game_states[room]['players'][player_id].is_active = False

