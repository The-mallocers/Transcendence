from typing import Any

import redis.asyncio as aioredis
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction
from redis.commands.json.path import Path

from apps.player.api.serializers import PlayerSerializer
from apps.player.models import Player
from utils.pong.enums import GameStatus
from utils.pong.objects import Ball, Paddle


class GameManager:
    _instance = None
    _redis = aioredis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    def __init__(self):
        from apps.game.models import Game
        self._game: Game = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = GameManager()
        return cls._instance

    async def create_game(self) -> Any | None:
        from apps.game.api.serializers import GameSerializer

        self._game = await self._create_game()
        serializer = GameSerializer(self._game, context={'ball': Ball()})

        key = f'game:{self._game.id}'
        value = await sync_to_async(lambda: serializer.data)()

        await self._redis.json().set(key, Path.root_path(), value)
        return self._game

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ADDER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def add_player(self, player_id):
        player = await self._get_player(player_id)
        await self._add_player(player)
        serializer = PlayerSerializer(player, context={'paddle': Paddle()})

        game = f'game:{self._game.id}'
        key = f'$.players'
        value = await sync_to_async(lambda: serializer.data)()

        await self._redis.json().arrappend(game, key, value)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SETTER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def set_status(self, status):
        self._game.status = status
        await self._update_status(status)

        # Update in Redis
        game_key = f'game:{self._game.id}'
        await self._redis.json().set(game_key, '$.status', status)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GETTER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def get_id(self):
        return self._game.id

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ASYNC ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    @sync_to_async
    def _create_game(self):
        from apps.game.models import Game
        with transaction.atomic():
            return Game.objects.create(in_tournament=False, status=GameStatus.CREATING)

    @sync_to_async
    def _get_player(self, id) -> Player:
        with transaction.atomic():
            return Player.objects.get(id=id)

    @sync_to_async
    def _add_player(self, player):
        with transaction.atomic():
            self._game.players.add(player)

    @sync_to_async
    def _update_status(self, status):
        with transaction.atomic():
            self._game.status = status
            self._game.save()

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