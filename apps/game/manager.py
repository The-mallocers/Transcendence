import asyncio
import traceback

from asgiref.sync import sync_to_async
from django.db import transaction, DatabaseError
from redis import DataError
from redis.commands.json.path import Path

from apps.game.models import Game
from apps.player.models import PlayerGame
from utils.pong.enums import GameStatus
from utils.pong.objects.ball import Ball
from utils.redis import RedisConnectionPool


class GameManager:
    def __init__(self, game=None, redis=None):
        from apps.game.models import Game
        from apps.player.manager import PlayerManager

        self._game: Game = game
        self._redis = RedisConnectionPool.get_sync_connection() if redis is not None else redis

        self.game_key = None if game is None else f'game:{game.id}'
        self.loop = asyncio.get_running_loop()
        self.pL: PlayerManager = None  # PlayerManager(self.rget_pL_id())
        self.pR: PlayerManager = None  # PlayerManager(self.rget_pR_id())

    async def create_game(self):
        from apps.game.api.serializers import GameSerializer
        self._redis = await RedisConnectionPool.get_async_connection(self.__class__.__name__)

        self._game = await self._create_game()
        self.game_key = f'game:{self._game.id}'

        serializer = GameSerializer(self._game, context={'ball': Ball()})
        value = await sync_to_async(lambda: serializer.data)()

        await self._redis.json().set(self.game_key, Path.root_path(), value)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Functions ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def error_game(self):
        await self.rset_status(GameStatus.ERROR)
        await self._redis.delete(f'game:{str(self._game.id)}')

    def get_id(self):
        if self._game:
            return self._game.id
        return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ REDIS OPERATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def rget_status(self) -> GameStatus | None:
        try:
            status = await self._redis.json().get(self.game_key, Path('status'))
            if status:
                return GameStatus(status)
            else:
                return None
        except DataError:
            traceback.print_exc()
            return None

    async def rset_status(self, status: GameStatus):
        if self.rget_status() != status:
            self._game.status = status
            await self._game.asave()
        await self._redis.json().set(self.game_key, Path('status'), status.value)

    async def rget_pL_id(self):
        try:
            return await self._redis.json().get(self.game_key, Path('players[0].id'))
        except DataError:
            return None

    async def rget_pR_id(self):
        try:
            return await self._redis.json().get(self.game_key, Path('players[1].id'))
        except DataError:
            return None

    async def rget_pL_score(self):
        try:
            return await self._redis.json().get(self.game_key, Path('players[0].score'))
        except DataError:
            return None

    async def rget_pR_score(self):
        try:
            return await self._redis.json().get(self.game_key, Path('players[1].score'))
        except DataError:
            return None

    async def set_result(self):
        score_pL = await self.rget_pL_score()
        score_pR = await self.rget_pR_score()
        if score_pL > score_pR:
            self._game.winner = self.pL.player
            self._game.loser = self.pR.player
        elif score_pL < score_pR:
            self._game.winner = self.pR.player
            self._game.loser = self.pL.player
        pL_game: PlayerGame = await self.pL.get_player_game_id_db(player_id=self.pL.id, game_id=self.get_id())
        pR_game: PlayerGame = await self.pR.get_player_game_id_db(player_id=self.pR.id, game_id=self.get_id())
        pL_game.score = score_pL
        pR_game.score = score_pR
        await pL_game.asave()
        await pR_game.asave()
        await self._game.asave()


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ DATABASE OPERATIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def get_game_db(self, game_id):
        """Load an existing game from the database."""
        from apps.game.models import Game
        try:
            return Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def get_game_db_async(game_id):
        """Load an existing game from the database."""
        from apps.game.models import Game
        try:
            return Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return None

    @sync_to_async
    def add_player_db(self, player):
        """Add a player to the game in the database."""
        try:
            with transaction.atomic():
                self._game.players.add(player)
        except:
            raise ValueError(f'Cannot add {player.id}')

    @sync_to_async
    def _create_game(self):
        """Create a new game in the database."""
        from apps.game.models import Game, GameStatus
        try:
            with transaction.atomic():
                return Game.objects.create(in_tournament=False, status=GameStatus.CREATING)
        except ValueError as e:
            return ValueError(f'Cannot create game: {str(e)}')

    @classmethod
    def clean_db(cls):
        try:
            Game.objects.filter(
                status__in=[
                    GameStatus.CREATING,
                    GameStatus.MATCHMAKING,
                    GameStatus.STARTING,
                    GameStatus.RUNNING,
                    GameStatus.ENDING,
                    GameStatus.DESTROYING
                ]
            ).delete()

            PlayerGame.objects.filter(game__status=GameStatus.ERROR.value).delete()

            existing_game_ids = set(Game.objects.values_list('id', flat=True))
            PlayerGame.objects.exclude(game_id__in=existing_game_ids).delete()
        except Exception as e:
            raise DatabaseError(f"Cannot clean games: {str(e)}")

    # async def update_ball(self, game_id, x, y):
    #     redis = await self.connect()
    #     key = f'game:{game_id}'
    #
    #     current_state = await redis.get(key)
    #     if current_state:
    #         state = json.loads(current_state)
    #         state['ball_position'] = {'x': x, 'y': y}
    #         await redis.set(key, json.dumps(state))
    #
    # async def update_player_score(self, game_id, player, score):
    #     redis = await self.connect()
    #     key = f'game:{game_id}'
    #
    #     current_state = await redis.get(key)
    #     if current_state:
    #         state = json.loads(current_state)
    #         state['scores'][player] = score
    #         await redis.set(key, json.dumps(state))
    #
    # async def get_game_state(self, game_id):
    #     redis = await self.connect()
    #     key = f'game:{game_id}'
    #
    #     state = await redis.get(key)
    #     return json.loads(state) if state else None
    #
    # async def get_all_game_ids(self):
    #     redis = await self.connect()
    #     keys = await redis.keys('game:*')
    #     return [key.decode().split(':')[1] for key in keys]
    #
    # async def end_game(self, game_id):
    #     redis = await self.connect()
    #     key = f'game:{game_id}'
    #
    #     current_state = await redis.get(key)
    #     if current_state:
    #         state = json.loads(current_state)
    #         state['status'] = 'finished'
    #         await redis.set(key, json.dumps(state))
    #         await redis.expire(key, 86400)