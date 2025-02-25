from enum import Enum


class GameStatus(str, Enum):
    CREATING: str = 'creating'
    MATCHMAKING: str = 'matchmaking'
    STARTING: str = 'starting'
    RUNNING: str = 'running'
    ENDING: str = 'ending'
    DESTROING: str = 'destroing'
    FINISHED: str = 'finished'
    ERROR: str = 'error'

class EventType(str, Enum):
    MATCHMAKING: str = 'matchmaking'
    GAME: str = 'game'
    ERROR: str = 'error'

#All the action the client send to server
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
    JOIN_QUEUE: str = 'join_queue'
    LEAVE_QUEUE: str = 'leave_queue'

#All the reponse the server send to client
class ResponseAction(str, Enum):
    JOIN_QUEUE: str = 'Successfuly join queue'
    LEFT_QUEUE: str = 'Successfuly left queue'
    JOIN_GAME: str = 'Successfuly join game'
    LEFT_GAME: str = 'Successfuly left game'


    TEST: str = 'test'

#All the error msg send to client
class ResponseError(str, Enum):
    GAME_FULL: str = 'Game full'
    ALREADY_JOIN: str = "Player has already join"
    NOT_IN_GAME: str = 'Player not int game'
    NOT_READY: str = 'Players is not ready'
    JOINING_ERROR: str = 'Error when you try to join'
    INVALID_ID: str = 'Player does not exist'
    MATCHMAKING_ERROR: str = 'Leaving matchmaking because there is an error'
    PLAYER_NOT_FOUND: str = 'Your id player corresponding to no player'
    JSON_ERROR: str = 'Invalid json'
    EXCEPTION: str = ''
    SERVICE_ERROR: str = ''

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