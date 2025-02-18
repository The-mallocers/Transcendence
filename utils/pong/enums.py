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
    ERROR: str = 'error'

class RequestType(str, Enum):
    MATCHMAKING: str = 'matchmaking'
    GAME: str = 'game'

class SendType(str, Enum):
    MATCHMAKING: str = 'matchmaking'


class RequestAction(str, Enum):
    # ── Game Actions ──────────────────────────────────────────────────────────────────
    JOIN_GAME: str = 'join_game'
    START_GAME: str = 'start_game'
    IS_READY: str = 'is_ready'
    PADDLE_MOVE: str = 'paddle_move'
    BALL_UPDATE: str = 'ball_update'
    P1_SCORE_UPDATE: str = 'p1_score_update'
    P2_SCORE_UPDATE: str = 'p2_score_update'

    # ── Matchmaking Actions ───────────────────────────────────────────────────────────
    JOIN_MM: str = 'join_matchmaking'
    LEAVE_MM: str = 'leave_matchmaking'

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