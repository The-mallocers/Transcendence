from dataclasses import dataclass

from redis.asyncio import Redis
from redis.commands.json.path import Path

from apps.player.models import Player


@dataclass
class Score:
    def __init__(self, game_id=None, redis=None, player_id=None):
        # ── Fields ────────────────────────────────────────────────────────────────────────
        self.score = 0

        # ── Utils ─────────────────────────────────────────────────────────────────────────    
        self.redis: Redis = redis
        self.game_key = RTables.JSON_GAME(game_id)
        self.player_id = player_id
        self.player_side = Player.get_player_side(self.player_id, self.game_key, self.redis)

    def update(self):
        self.score = self.get_score()

    def get_score(self):
        return self.redis.json().get(RTables.JSON_GAME(self.game_key), Path(f'player_{self.player_side}.score'))

    def add_score(self):
        current = self.get_score()
        self.redis.json().set(RTables.JSON_GAME(self.game_key), Path(f'player_{self.player_side}.score'), current + 1)
        self.score += 1

    def del_score(self):
        current = self.get_score()
        self.redis.json().set(RTables.JSON_GAME(self.game_key), Path(f'player_{self.player_side}.score'), current - 1)
        self.score -= 1

    def set_score(self, score):
        self.redis.json().set(RTables.JSON_GAME(self.game_key), Path(f'player_{self.player_side}.score'), score)
        self.score = score
