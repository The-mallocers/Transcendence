import logging
import random

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction
from redis.asyncio import Redis
from redis.commands.json.path import Path

from apps.game.manager import GameManager
from apps.player.api.serializers import PlayerSerializer
from apps.player.models import Player
from apps.player.models import PlayerGame
from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseError, ResponseAction, Side
from utils.pong.objects.paddle import Paddle
from utils.websockets.channel_send import send_group_error, send_group


class PlayerManager:
    def __init__(self):
        self._redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self._logger = logging.getLogger(self.__class__.__name__)

        self._player_game: PlayerGame = None
        self._player: Player = None
        self.id = None
        self.paddle: Paddle = None

    async def init_player(self, player_id, game_id=None):
        player = await self.get_player_db(player_id)
        if player:
            self._player = player
            self.paddle = Paddle(self._redis, player_id=player.id, game_id=game_id)
            self.id = player_id
            return self
        else:
            return None

    async def join_game(self, game_manager: GameManager):
        try:
            await game_manager.add_player_db(self._player)
            self._player_game: PlayerGame = await self.get_player_game_id_db(self._player.id, await game_manager.get_id())

            game_key = f'game:{await game_manager.get_id()}'
            players = await self._redis.json().get(game_key, Path("players"))
            player_ids = [player["id"] for player in players]

            if self._player.id in player_ids:
                return await send_group_error(self._player.id, ResponseError.ALREADY_JOIN)
            else:
                if len(player_ids) == 0:
                    rand_side = random.choice(list(Side))
                    self._player_game.side = rand_side
                elif len(player_ids) == 1:
                    first_player: PlayerGame = await self.get_player_game_id_db(str(player_ids[0]), await game_manager.get_id())
                    if first_player.side == Side.RIGHT.value:
                        self._player_game.side = Side.LEFT
                    if first_player.side == Side.LEFT.value:
                        self._player_game.side = Side.RIGHT
                elif len(player_ids) == 2:
                    return await send_group_error(self._player.id, ResponseError.GAME_FULL)
                await sync_to_async(self._player_game.save)()

            # ── Send Reponse To Player ────────────────────────────────────────────────

            self.paddle.game_key = game_key
            serializer = PlayerSerializer(self._player, context={'paddle': self.paddle, 'side': self._player_game.side})
            player_data = await sync_to_async(lambda: serializer.data)()

            await self._redis.json().arrappend(game_key, Path("players"), player_data)

            channel_layer = get_channel_layer()
            client = await Clients.get_client_by_player(self._player.id)
            channel_name = await self._redis.hget(name="consumers_channels", key=str(client.id))
            await channel_layer.group_add(str(await game_manager.get_id()), channel_name.decode('utf-8'))

            await send_group(self._player.id, EventType.GAME, ResponseAction.JOIN_GAME)
            await self.leave_mm()

        except Exception as e:
            await send_group_error(self._player.id, ResponseError.JOINING_ERROR)
            await self.leave_mm()
            raise RuntimeError(str(e))


    def __str__(self):
        return f"{self._player}"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ DATABASE OPERATIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ── Getter ────────────────────────────────────────────────────────────────────────

    @sync_to_async
    def get_player_db(self, player_id):
        """Get player from data base"""
        try:
            with transaction.atomic():
                return Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return None

    @sync_to_async
    def get_player_game_id_db(self, player_id, game_id) -> PlayerGame | None:
        """Get player game with player_id from data base"""
        try:
            with transaction.atomic():
                return PlayerGame.objects.get(player__id=player_id, game__id=game_id)
        except PlayerGame.DoesNotExist:
            return None

    @sync_to_async
    def get_player_from_client_db(self, client_id) -> Player | None:
        """Get player with client id from data base"""
        try:
            with transaction.atomic():
                return Clients.objects.select_related('player__stats').get(
                    id=client_id).player
        except Clients.DoesNotExist:
            return None

    async def leave_mm(self):
        await self._redis.hdel('matchmaking_queue', str(self._player.id))