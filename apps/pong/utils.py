import time
from dataclasses import dataclass
from enum import Enum

BALL_SPEED = 2
PADDLE_SPEED = 10
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_RADIUS = 2
FPS = 60
OFFSET_PADDLE = 25
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 500

class GameState:
    def __init__(self, id: str):
        from apps.player.models import Player
        self.id: str = id
        self.task = None
        self.ball: Ball = Ball()
        self.game_active: bool = False
        self.last_update: float = time.time()
        self.game_status: GameStatus = GameStatus.CREATING
        self.player_1: Player = None
        self.player_2: Player = None

    def to_dict(self):
        return {
            'p1_paddle': self.player_1.paddle_y,
            'p2_paddle': self.player_2.paddle_y,
            'p1_score': self.player_1.score,
            'p2_score': self.player_2.score,
            'ball_x': self.ball.x,
            'ball_y': self.ball.y,
            'game_active': self.game_active
        }

    def __str__(self):
        return f"Game state id: {str(self.id)}\nIs active: {self.game_active}\nPlayer 1: {self.player_1}\nPlayer 2: {self.player_2}\n-------------------"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ENUMS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

class GameStatus(int, Enum):
    CREATING: int = 0
    MATCHMAKING: int = 1
    WAITING: int = 2
    GAMING: int = 3
    ENDING: int = 4
    DESTROING: int = 5

class RequestType(str, Enum):
    JOIN_GAME = 'join_game'
    PADDLE_MOVE = 'paddle_move'
    GAME_STATE = 'game_state'
    PLAYER_ACTION = 'player_action'

class ErrorType(str, Enum):
    GAME_FULL = 'Game full'
    ALREADY_JOIN = "Player has already join"
    NOT_IN_GAME = 'Player not int game'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ OBJECTS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Ball:
    radius: float = BALL_RADIUS
    x: float = CANVAS_WIDTH / 2
    y: float = CANVAS_HEIGHT / 2
    dx: float = BALL_SPEED
    dy: float = BALL_SPEED

@dataclass
class Paddle:
    width:float = PADDLE_WIDTH
    height:float = PADDLE_HEIGHT
    x:float = 0
    y:float = 0
    speed:float = PADDLE_SPEED