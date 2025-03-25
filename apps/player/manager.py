import logging
import random

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.db import transaction
from redis.commands.json.path import Path

from apps.game.manager import GameManager
from apps.player.api.serializers import PlayerSerializer
from apps.player.models import Player
from apps.player.models import PlayerGame
from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseError, ResponseAction, Side
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score
from utils.redis import RedisConnectionPool
from utils.websockets.channel_send import send_group_error, send_group


class PlayerManager:
    def __init__(self, player_id, game_id=None, redis=None):
        self._redis = redis
        self._logger = logging.getLogger(self.__class__.__name__)
        self._player_game: PlayerGame = None

        self.player = None  # asyncio.create_task(self.get_player_db(player_id))
        self.id = player_id
        self.paddle: Paddle = Paddle(self._redis, player_id=self.id, game_id=game_id)
        self.score: Score = Score(self._redis, player_id=self.id, game_id=game_id)

    async def join_game(self, game_manager: GameManager):
        #We will only want to join with Redis, not add to DB.
        try:
            self._redis = await RedisConnectionPool.get_async_connection(self.__class__.__name__)
            self.paddle._redis = self._redis
            self.score._redis = self._redis
            self.player = await self.get_player_db(self.id)
            await game_manager.add_player_db(self.player)
            self._player_game: PlayerGame = await self.get_player_game_id_db_async(self.player.id, game_manager.get_id())

            game_key = f'game:{game_manager.get_id()}'
            players = await self._redis.json().get(game_key, Path("players"))
            player_ids = [player["id"] for player in players]

            #This is just to find a side.
            if self.player.id in player_ids:
                return await send_group_error(self.player.id, ResponseError.ALREADY_JOINED)
            else:
                if len(player_ids) == 0:
                    rand_side = random.choice(list(Side))
                    self._player_game.side = rand_side
                elif len(player_ids) == 1:
                    first_player: PlayerGame = await self.get_player_game_id_db_async(str(player_ids[0]), game_manager.get_id())
                    if first_player.side == Side.RIGHT.value:
                        self._player_game.side = Side.LEFT
                    if first_player.side == Side.LEFT.value:
                        self._player_game.side = Side.RIGHT
                elif len(player_ids) == 2:
                    return await send_group_error(self.player.id, ResponseError.GAME_FULL)
                await sync_to_async(self._player_game.save)()

            # ── Send Reponse To Player ────────────────────────────────────────────────
            #this wont really change.
            self.paddle.game_key = game_key
            serializer = PlayerSerializer(self.player,
                                          context={'paddle': self.paddle, 'side': self._player_game.side, 'score': self.score.score})
            player_data = await sync_to_async(lambda: serializer.data)()

            await self._redis.json().arrappend(game_key, Path("players"), player_data)

            channel_layer = get_channel_layer()
            client = await Clients.get_client_by_player_id_async(self.player.id)
            channel_name = await self._redis.hget(name="consumers_channels", key=str(client.id))
            await channel_layer.group_add(str(game_manager.get_id()), channel_name.decode('utf-8'))

            await send_group(self.player.id, EventType.GAME, ResponseAction.JOIN_GAME)
            await self.leave_mm()

        except Exception as e:
            await send_group_error(self.player.id, ResponseError.JOINING_ERROR)
            await self.leave_mm()
            raise RuntimeError(str(e))


    def __str__(self):
        return f"{self.player}"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ DATABASE OPERATIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ── Getter ────────────────────────────────────────────────────────────────────────

    @staticmethod
    @sync_to_async
    def get_player_db(player_id):
        """Get player from data base"""
        try:
            return Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return None

    @sync_to_async
    def get_player_db_async(self, player_id):
        """Get player from data base"""
        try:
            with transaction.atomic():
                return Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def get_player_game_id_db_async(player_id, game_id) -> PlayerGame | None:
        """Get player game with player_id from data base"""
        try:
            with transaction.atomic():
                return PlayerGame.objects.get(player__id=player_id, game__id=game_id)
        except PlayerGame.DoesNotExist:
            return None
                
    @staticmethod
    def get_player_game_id_db(player_id, game_id) -> PlayerGame | None:
        """Get player game with player_id from data base"""
        try:
            with transaction.atomic():
                return PlayerGame.objects.get(player__id=player_id, game__id=game_id)
        except PlayerGame.DoesNotExist:
            return None

    @sync_to_async
    def get_player_from_client_db_async(self, client_id) -> Player | None:
        """Get player with client id from data base"""
        try:
            with transaction.atomic():
                return Clients.objects.select_related('player__stats').get(
                    id=client_id).player
        except Clients.DoesNotExist:
            return None
        
    @staticmethod
    def get_player_from_client_db(client_id) -> Player | None:
        """Get player with client id from data base"""
        try:
            return Clients.objects.get(id=client_id).player
        except Clients.DoesNotExist:
            return None

    async def leave_mm(self):
        await self._redis.hdel('matchmaking_queue', str(self.player.id))
