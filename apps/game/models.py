import asyncio
from datetime import timedelta
from typing import Dict

import redis
from channels.db import database_sync_to_async
from django.db import models
from django.db.models import IntegerField, ForeignKey, CharField, \
    ManyToManyField
from django.db.models.fields import BooleanField, DurationField, DateTimeField
from django.utils import timezone

from apps.game.manager import GameManager
from apps.player.manager import PlayerManager
from apps.player.models import Player, PlayerGame
from apps.pong.api.serializers import PaddleSerializer
from apps.pong.utils import GameState
from apps.shared.models import Clients
from utils.pong.enums import RequestType, GameStatus, ErrorType
from utils.utils import generate_unique_code

redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class Game(models.Model):
    class Meta:
        db_table = 'pong_games'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ PRIMARY FIEDLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = IntegerField(primary_key=True, editable=False, null=False, default=generate_unique_code, unique=True)

    # ── Game Informations ───────────────────────────────────────────────────────────── #
    created_at = DateTimeField(default=timezone.now)
    in_tournament = BooleanField(editable=False, default=False, null=False)
    winner = ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='winner', editable=False, blank=True)

    # ── Game Settings ───────────────────────────────────────────────────────────── #
    status = CharField(max_length=20, choices=[(status.name, status.value) for status in GameStatus], default=GameStatus.CREATING.value)
    players = ManyToManyField(Player, through='player.PlayerGame')
    timer = DurationField(default=timedelta(minutes=0), editable=False, null=True) #In default there is no timer

class GameService:
    def __init__(self):
        self.game_manager = GameManager()
        self.player1_manager = PlayerManager()
        self.player2_manager = PlayerManager()

    async def process_action(self, player: Player, data: Dict, game: Game):
        request_type: RequestType = RequestType(data.get('type'))
        handlers = {
            RequestType.JOIN_GAME: self._handle_join_game,
            RequestType.PADDLE_MOVE: self._handle_paddle_move,
            RequestType.START_GAME: self._handle_start_game,
            RequestType.IS_READY: self._handle_is_ready,
        }

        if request_type in handlers:
            return await handlers[request_type](data, game, player)
        else:
            raise ValueError(f'Unknown action: {request_type}')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ HANDLES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

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
            'type': RequestType.JOIN_GAME,
            'player_id': str(player.id)
        }

    async def _handle_paddle_move(self, data: Dict, game: GameState, player: Player):
        if player == game.player_1 or player == game.player_2:
            await player.move(data.get('direction'))
            return {
                'type': RequestType.PADDLE_MOVE,
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
                'type': RequestType.IS_READY,
                'player_id': player.id,
                'is_ready': player.is_ready
            }

    async def _handle_start_game(self, data: Dict, game: GameState, player: Player):
        if game.player_1.is_ready and game.player_2.is_ready:
            game.active = True
            game.task = asyncio.create_task(self._game_task(game))
            return {
                'type': RequestType.START_GAME,
            }
        else:
            return {
                'error': ErrorType.NOT_READY
            }

    async def handle_disconnect(self, room: str, player_id: str):
        if room in self.game_states and player_id in \
                self.game_states[room]['players']:
            self.game_states[room]['players'][player_id].is_active = False


