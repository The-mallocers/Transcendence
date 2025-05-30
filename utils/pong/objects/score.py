from dataclasses import dataclass

from redis.asyncio import Redis
from redis.commands.json.path import Path

from apps.player.models import Player
from utils.enums import PlayerSide, RTables


@dataclass
class Score:
    def __init__(self, side: PlayerSide, game_id=None, redis=None, client_id=None):
        # ── Fields ────────────────────────────────────────────────────────────────────────
        self.score = 0

        # ── Utils ─────────────────────────────────────────────────────────────────────────    
        self.redis: Redis = redis
        self.game_key = RTables.JSON_GAME(game_id)
        self.player_side = side.value

    def update(self):
        self.score = self.get_score()

    def push_to_redis(self):
        self.set_score(self.score)
    

    def get_score(self):
        return self.redis.json().get(self.game_key, Path(f'{self.player_side}.score'))

    def add_score(self):
        current = self.get_score()
        self.redis.json().set(self.game_key, Path(f'{self.player_side}.score'), current + 1)
        self.score += 1

    def del_score(self):
        current = self.get_score()
        self.redis.json().set(self.game_key, Path(f'{self.player_side}.score'), current - 1)
        self.score -= 1

    def set_score(self, score):
        self.redis.json().set(self.game_key, Path(f'{self.player_side}.score'), score)
        self.score = score
