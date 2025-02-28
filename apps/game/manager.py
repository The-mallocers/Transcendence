from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction, DatabaseError
from redis.asyncio import Redis
from redis.commands.json.path import Path

from apps.game.models import Game
from apps.player.models import PlayerGame
from utils.pong.enums import GameStatus
from utils.pong.objects.ball import Ball


class GameManager:
    def __init__(self, game_id = None):
        from apps.game.models import Game
        from apps.player.manager import PlayerManager
        self._redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self._game: Game = None
        self.p1: PlayerManager = PlayerManager()
        self.p2: PlayerManager = PlayerManager()
        self._game_key = None

        if game_id:
            self.load_by_id(game_id)

    async def load_by_id(self, game_id):
        from apps.game.models import Game
        self._game = await Game.objects.aget(id=game_id)
        self._game_key = f"game:{game_id}"
        await self.p1.init_player(await self.rget_player1_id(), game_id)
        await self.p2.init_player(await self.rget_player2_id(), game_id)

    async def create_game(self):
        """Create a new game and store it in Redis."""
        from apps.game.api.serializers import GameSerializer

        self._game = await self._create_game()

        serializer = GameSerializer(self._game, context={'ball': Ball()})
        self._game_key = f'game:{self._game.id}'
        value = await sync_to_async(lambda: serializer.data)()

        await self._redis.json().set(self._game_key, Path.root_path(), value)

    async def init_game_manager(self, game_id, redis):
        self._game = await self.get_game_db(game_id)
        if self._game:
            self._redis = redis
            self._game_key = f'game:{self._game.id}'
            return
        else:
            raise ValueError(f'This game does not exist: {game_id}')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Functions ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def error_game(self):
        await self.rset_status(GameStatus.ERROR)
        await self._redis.delete(f'game:{str(self._game.id)}')

    async def get_id(self):
        if self._game:
            return self._game.id
        return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ REDIS OPERATION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def rget_status(self) -> GameStatus | None:
        status = await self._redis.json().get(self._game_key, Path('status'))
        if status:
            return GameStatus(status)
        else:
            return None

    async def rset_status(self, status: GameStatus):
        if self.rget_status() != status:
            self._game.status = status
            await self._game.asave()
        await self._redis.json().set(self._game_key, Path('status'), status.value)

    async def rget_player1_id(self):
        return await self._redis.json().get(self._game_key, Path('players[0].id'))

    async def rget_player2_id(self):
        return await self._redis.json().get(self._game_key, Path('players[1].id'))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ DATABASE OPERATIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    @sync_to_async
    def get_game_db(self, game_id):
        """Load an existing game from the database."""
        from apps.game.models import Game
        try:
            with transaction.atomic():
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
                    GameStatus.DESTROING
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