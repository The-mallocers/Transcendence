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
    CHAT = "chat"
    MATCHMAKING: str = 'matchmaking'
    GAME: str = 'game'
    UPDATE: str = 'update'
    ERROR: str = 'error'
    CHAT: str = 'chat'

#All the action the client send to server
class RequestAction(str, Enum):
    # ── Matchmaking Actions ───────────────────────────────────────────────────────────
    JOIN_QUEUE: str = 'join_queue'
    LEAVE_QUEUE: str = 'leave_queue'

    # ── Game Actions ──────────────────────────────────────────────────────────────────
    JOIN_GAME: str = 'join_game'
    START_GAME: str = 'start_game'
    STOP_GAME: str = 'stop_game'

    IS_READY: str = 'is_ready'
    # ── Update ────────────────────────────────────────────────────────────────────────
    BALL_UPDATE: str = 'ball_update'
    PADDLE_MOVE: str = 'paddle_move'
    SCORE_UPDATE: str = 'score_update'

    # ── Chat Actions ──────────────────────────────────────────────────────────────────
    START_CHAT = "start_chat"
    SEND_MESSAGE = "send_message"


#All the reponse the server send to client
class ResponseAction(str, Enum):
    # ── Matchmaking Actions ───────────────────────────────────────────────────────────
    JOIN_QUEUE: str = 'Successfuly join queue'
    LEFT_QUEUE: str = 'Successfuly left queue'

    # ── Game Actions ──────────────────────────────────────────────────────────────────
    JOIN_GAME: str = 'Successfuly join game'
    LEFT_GAME: str = 'Successfuly left game'
    STARTING: str = 'Waiting to game start'
    STARTED: str = 'Game will start'
    ENDING: str = 'Game end'

    # ── Update ────────────────────────────────────────────────────────────────────────
    BALL_UPDATE: str = 'ball_update'
    PADDLE_1_UPDATE: str = 'paddle_1_update'
    PADDLE_2_UPDATE: str = 'paddle_2_update'
    SCORE_1_UPDATE: str = 'score_1_update'
    SCORE_2_UPDATE: str = 'score_2_update'

    # ── Chat Actions ──────────────────────────────────────────────────────────────────
    CHAT_STARTED = "chat_started"
    MESSAGE = "message"
    MESSAGE_SENT = "message_sent"


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
    PLAYER_NOT_FOUND: str = 'Your player id not corresponding to a player'
    JSON_ERROR: str = 'Invalid json'
    EXCEPTION: str = 'Internal server error'
    INTERNAL_ERROR = "Internal server error"
    ACTION_ERROR: str = 'Action error'

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