from enum import Enum

class GameStatus(str, Enum):
    CREATING: str = 'creating'
    MATCHMAKING: str = 'matchmaking'
    STARTING: str = 'starting'
    RUNNING: str = 'running'
    ENDING: str = 'ending'
    DESTROYING: str = 'destroying'
    FINISHED: str = 'finished'
    ERROR: str = 'error'


status_order = list(GameStatus)

class TournamentStatus(str, Enum):
    CREATING: str = 'creating'
    MATCHMAKING: str = 'matchmaking'
    STARTING: str = 'starting'
    RUNNING: str = 'running'
    ENDING: str = 'ending'
    DESTROYING: str = 'destroying'
    FINISHED: str = 'finished'
    ERROR: str = 'error'

class EventType(str, Enum):
    MATCHMAKING: str = 'matchmaking'
    GAME: str = 'game'
    TOURNAMENT: str = 'tournament'
    UPDATE: str = 'update'
    ERROR: str = 'error'
    CHAT: str = 'chat'
    NOTIFICATION: str = 'notification'

# All the actions the client sends to the server
class RequestAction(str, Enum):
    # ── Matchmaking Actions ───────────────────────────────────────────────────────────
    JOIN_QUEUE: str = 'join_queue'
    LEAVE_QUEUE: str = 'leave_queue'

    # ── Game Actions ──────────────────────────────────────────────────────────────────
    JOIN_GAME: str = 'join_game'
    START_GAME: str = 'start_game'
    STOP_GAME: str = 'stop_game'

    # ── Update ────────────────────────────────────────────────────────────────────────
    PADDLE_MOVE: str = 'paddle_move'

    # ── Chat Actions ──────────────────────────────────────────────────────────────────
    CREATE_ROOM: str = "create_room"
    SEND_MESSAGE: str = "send_message"
    GET_HISTORY: str = "get_history"
    GET_ALL_ROOM_BY_CLIENT: str = "get_all_room_by_client"

    # ── Tournament ────────────────────────────────────────────────────────────────────
    CREATE_TOURNAMENT: str = 'create_tournament'
    JOIN_TOURNAMENT: str = 'join_tournament'
    LEAVE_TOURNAMENT: str = 'leave_tournament'
    START_TOURNAMENT: str = 'start_tournement'
    LIST_TOURNAMENT: str = 'list_tournament'
    
    # ── Notification Actions ──────────────────────────────────────────────────────────────────
    SEND_FRIEND_REQUEST: str = "send_friend_request"
    ACCEPT_FRIEND_REQUEST: str = "accept_friend_request"
    REFUSE_FRIEND_REQUEST: str = "refuse_friend_request"
    DELETE_FRIEND: str = "delete_friend"
    


# All the responses the server sends to the client
class ResponseAction(str, Enum):
    # ── Matchmaking Actions ───────────────────────────────────────────────────────────
    JOIN_QUEUE: str = 'You have successfully joined the queue'
    LEFT_QUEUE: str = 'You have successfully left the queue'

    # ── Game Actions ──────────────────────────────────────────────────────────────────
    JOIN_GAME: str = 'You have successfully joined the game'
    LEFT_GAME: str = 'You have successfully left the game'
    STARTING: str = 'The game is about to start'
    STARTED: str = 'The game has started'
    GAME_ENDING: str = 'The game has ended'

    # ── Update ────────────────────────────────────────────────────────────────────────
    PLAYER_INFOS: str = 'player_informations'
    BALL_UPDATE: str = 'ball_update'
    PADDLE_LEFT_UPDATE: str = 'paddle_left_update'
    PADDLE_RIGHT_UPDATE: str = 'paddle_right_update'
    SCORE_LEFT_UPDATE: str = 'score_left_update'
    SCORE_RIGHT_UPDATE: str = 'score_right_update'

    # ── Chat Actions ──────────────────────────────────────────────────────────────────
    ROOM_CREATED = "You have successfully created a chat room"
    MESSAGE_RECEIVED = "New message received"
    HISTORY_RECEIVED = "history_received"
    ALL_ROOM_RECEIVED = "all_room_received"
    
    # ── NOTIFICATION ACTION ───────────────────────────────────────────────────────────
    ACK_SEND_FRIEND_REQUEST: str = "acknowledge_send_friend_request"
    ACK_ACCEPT_FRIEND_REQUEST: str = "acknowledge_accept_friend_request"
    ACK_ACCEPT_FRIEND_REQUEST_HOST: str = "acknowledge_accept_friend_request_host"
    ACK_REFUSE_FRIEND_REQUEST: str = "acknowledge_refuse_friend_request"
    ACK_DELETE_FRIEND: str = "ack_delete_friend"
    ACK_DELETE_FRIEND_HOST: str = "ack_delete_friend_host"

    NOTIF_TEST = "notification_test"
    

    TEST: str = 'test'


# All the error messages sent to the client
class ResponseError(str, Enum):
    # ── Matchmaking ───────────────────────────────────────────────────────────────────
    ALREADY_IN_QUEUE: str = 'You are already in the queue.'
    ALREAY_IN_GAME: str = 'You are already in game.'
    NOT_IN_QUEUE: str = 'You are not currently in the queue.'
    MATCHMAKING_ERROR: str = 'Leaving matchmaking due to an error.'

    # ── Game ──────────────────────────────────────────────────────────────────────────
    GAME_FULL: str = 'The game is currently full.'
    ALREADY_JOINED: str = "You have already joined the game."
    ALREADY_START: str = 'The game has already started.'
    JOINING_ERROR: str = 'Error occurred while trying to join.'
    OPPONENT_LEFT: str = 'Your opponent has left the game.'
    NOT_READY_TO_START: str = 'The game is not ready to start yet.'
    NO_GAME: str = 'There is no active game'

    # ── Chat ──────────────────────────────────────────────────────────────────────────
    NO_HISTORY: str = 'There are no messages in this room.'

    # ── Notification ──────────────────────────────────────────────────────────────────────────
    USER_NOT_FOUND: str = 'User not found'
    USER_ALREADY_MY_FRIEND: str = 'User already my friend'
    USER_ALREADY_FRIEND_OR_NOT_PENDING_FRIEND: str = 'User already friend or not in pending list'
    NOT_FRIEND: str = "not_friend"
    INTERNAL_ERROR: str = "internal_error"

    # ── Errors ────────────────────────────────────────────────────────────────────────
    PLAYER_NOT_FOUND: str = 'Your player ID does not correspond to a player.'
    JSON_ERROR: str = 'There is an error in JSON decoding.'
    EXCEPTION: str = 'An error has occurred.'
    SERVICE_ERROR: str = 'An error occurred in the service.'

    # INTERNAL_ERROR = "Internal server error"
    # INVALID_ID: str = 'Player does not exist'
    # NOT_READY: str = 'Players are not ready'
    # NOT_IN_GAME: str = 'Player is not in the game'
    ROOM_NOT_FOUND: str = 'Room does not exist'
    NOT_ALLOWED: str = 'You are not allowed to send message'
    TARGET_NOT_FOUND: str = 'Target not found'
    SAME_ID: str = 'You can\'t create room with yourself'


class Side(str, Enum):
    LEFT: str = 'left'
    RIGHT: str = 'right'

class PaddleMove(str, Enum):
    UP: str = 'up'
    DOWN: str = 'down'
    IDLE: str = 'idle'


class Ranks(str, Enum):
    BRONZE: str = 'bronze'
    SILVER: str = 'silver'
    GOLD: str = 'gold'
    PLATINUM: str = 'platinum'
    DIAMOND: str = 'diamond'
    CHAMPION: str = 'champion'
