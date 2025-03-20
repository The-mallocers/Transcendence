import logging
from dataclasses import dataclass

from redis.asyncio import Redis
from redis.commands.json.path import Path


@dataclass
class Score:
    def __init__(self, redis=None, game_id=None, player_id=None):
        self.score = 0
        self._redis: Redis = redis
        self.game_key = f'game:{game_id}'
        self.player_id = player_id

    async def update(self):
        self.score = await self.get_score()

    async def get_score(self):
        return await self._redis.json().get(self.game_key, Path('players[?(@.id=="{}")].score'.format(self.player_id)))

    async def add_score(self):
        current = await self.get_score()
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].score'.format(self.player_id)), current + 1)
        self.score += 1

    async def del_score(self):
        current = await self.get_score()
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].score'.format(self.player_id)), current - 1)
        self.score -= 1