import copy
import time

from utils.pong.enums import GameStatus
from utils.pong.objects import ball


class GameState:
    def __init__(self, id: str):
        from apps.player.models import Player
        self.id: str = id
        self.task = None
        self.ball: Ball = Ball()
        self.active: bool = False
        self.last_update: float = time.time()
        self.status: GameStatus = GameStatus.CREATING
        self.player_1: Player = None
        self.player_2: Player = None

    def get_snapshot(self):
        return {
            "ball": copy.deepcopy(self.ball),
            "p1_score": self.player_1.score if self.player_1 else None,
            "p2_score": self.player_2.score if self.player_2 else None,
            "p1_paddle": copy.deepcopy(self.player_1.paddle),
            "p2_paddle": copy.deepcopy(self.player_2.paddle)
        }

    def __str__(self):
        return f"Game state id: {str(self.id)}\nIs active: {self.active}\nPlayer 1: {self.player_1}\nPlayer 2: {self.player_2}\n-------------------"
