from enum import Enum


class GameStatus(str, Enum):
    CREATING: str = 'creating'
    WAITING: str = 'waiting'
    MATCHMAKING: str = 'matchmaking'
    STARTING: str = 'starting'
    RUNNING: str = 'running'
    ENDING: str = 'ending'
    DESTROING: str = 'destroing'
    FINISHED: str = 'finished'

class RequestType(str, Enum):
    JOIN_GAME = 'join_game'
    START_GAME = 'start_game'
    IS_READY = 'is_ready'
    PADDLE_MOVE = 'paddle_move'
    BALL_UPDATE = 'ball_update'
    P1_SCORE_UPDATE = 'p1_score_update'
    P2_SCORE_UPDATE = 'p2_score_update'

class ErrorType(str, Enum):
    GAME_FULL = 'Game full'
    ALREADY_JOIN = "Player has already join"
    NOT_IN_GAME = 'Player not int game'
    NOT_READY = 'Players is not ready'

class Side(str, Enum):
    LEFT: str = 'left'
    RIGHT: str = 'right'

class Ranks(str, Enum):
    BRONZE: str = 'bronze'
    SILVER: str = 'silver'
    GOLD: str = 'gold'
    PLATINE: str = 'platine'
    DIAMOND: str = 'diamond'
    CHAMPION: str = 'champion'