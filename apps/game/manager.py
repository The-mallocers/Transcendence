import asyncio
import logging

from redis.asyncio import Redis
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction
from redis.commands.json.path import Path

from apps.player.api.serializers import PlayerSerializer
from utils.pong.objects import Ball, Paddle


class GameManager:
    _instances = {}
    _redis_connections = {}  # Store Redis connections per loop

    def __init__(self, game_id = None):
        from apps.game.models import Game
        self._game: Game = None
        self.game_id = game_id

    @classmethod
    async def get_instance(cls, game_id=None):
        """Get or create a GameManager instance for a specific game."""
        if game_id is None:
            return GameManager()  # Temporary instance
        if game_id not in cls._instances:
            instance = GameManager(game_id)
            instance._game = await instance.get_game_db(game_id)
            cls._instances[game_id] = instance
        return cls._instances[game_id]

    @classmethod
    async def get_redis(cls):
        """Get or create Redis connection for current event loop"""
        loop = asyncio.get_running_loop()
        if loop not in cls._redis_connections:
            cls._redis_connections[loop] = await Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True
            )
        return cls._redis_connections[loop]

    @classmethod
    async def cleanup(cls):
        """Cleanup Redis connections"""
        for redis in cls._redis_connections.values():
            await redis.close()
        cls._redis_connections.clear()

    async def create_game(self):
        """Create a new game and store it in Redis."""
        from apps.game.api.serializers import GameSerializer

        self._game = await self._create_game()
        self.game_id = self._game.id
        GameManager._instances[self.game_id] = self  # Register instance

        serializer = GameSerializer(self._game, context={'ball': Ball()})
        key = f'game:{self._game.id}'
        value = await sync_to_async(lambda: serializer.data)()

        redis = await self.get_redis()
        await redis.json().set(key, Path.root_path(), value)

    async def add_player(self, player_id):
        """Add a player to the game and update Redis."""
        player = await self._get_player(player_id)

        if player is None:
            raise

        await self._add_player(player)
        serializer = PlayerSerializer(player, context={'paddle': Paddle()})

        game_key = f'game:{self._game.id}'
        key = "$.players"
        value = await sync_to_async(lambda: serializer.data)()

        redis = await self.get_redis()
        await redis.json().arrappend(game_key, key, value)


    async def set_status(self, status):
        """Update game status and reflect in Redis."""
        if status == self._game.status:
            return

        # Update local instance
        self._game.status = status
        await self._update_status(status)

        try:
            # Get Redis connection for current loop
            redis = await self.get_redis()
            game_key = f'game:{self._game.id}'
            await redis.json().set(game_key, '$.status', status)
        except Exception as e:
            logging.error(f"Error updating Redis status: {e}")
            pass

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GETTER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def get_id(self):
        return self._game.id

    async def get_status(self):
        return self._game.status

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ DATABASE OPERATIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ── Getter ────────────────────────────────────────────────────────────────────────

    @sync_to_async
    def _get_player(self, id):
        """Retrieve a player from the database."""
        from apps.game.models import Player
        try:
            with transaction.atomic():
                return Player.objects.get(id=id)
        except Player.DoesNotExist:
            return None

    @sync_to_async
    def get_game_db(self, game_id):
        """Load an existing game from the database."""
        from apps.game.models import Game
        try:
            with transaction.atomic():
                return Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return None

    # ── Setter ────────────────────────────────────────────────────────────────────────

    @sync_to_async
    def _add_player(self, player):
        """Add a player to the game in the database."""
        try:
            with transaction.atomic():
                self._game.players.add(player)
        except:
            raise ValueError(f'Cannot add {player.id}')

    @sync_to_async
    def _update_status(self, status):
        """Update the game status in the database."""
        try:
            with transaction.atomic():
                self._game.status = status
                self._game.save()
        except:
            raise ValueError(f'Cannot update status to {status}')

    @sync_to_async
    def _create_game(self):
        """Create a new game in the database."""
        from apps.game.models import Game, GameStatus
        try:
            with transaction.atomic():
                return Game.objects.create(in_tournament=False, status=GameStatus.CREATING)
        except ValueError as e:
            return ValueError(f'Cannot create game: {str(e)}')

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