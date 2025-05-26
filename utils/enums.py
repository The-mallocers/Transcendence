from enum import Enum


class GameStatus(str, Enum):
    CREATING: str = 'creating'
    WAITING: str = 'waiting'
    MATCHMAKING: str = 'matchmaking'
    STARTING: str = 'starting'
    WAITING_TO_START: str = 'waiting_to_start'
    RUNNING: str = 'running'
    ENDING: str = 'ending'
    FINISHED: str = 'finished'
    ERROR: str = 'error'


game_status_order = list(GameStatus)

class TournamentStatus(str, Enum):
    CREATING: str = 'creating'
    WAITING: str = 'waiting'
    STARTING: str = 'starting'
    RUNNING: str = 'running'
    ENDING: str = 'ending'
    FINISHED: str = 'finished'
    ERROR: str = 'error'


class EventType(str, Enum):
    # ── Services ──────────────────────────────────────────────────────────────────────
    MATCHMAKING: str = 'matchmaking'
    GAME: str = 'game'
    TOURNAMENT: str = 'tournament'
    CHAT: str = 'chat'
    NOTIFICATION: str = 'notification'

    # ── Others ────────────────────────────────────────────────────────────────────────
    UPDATE: str = 'update'
    ERROR: str = 'error'


class SessionType(str, Enum):
    FINGERPRINT: str = 'fingerprint'
    SESSION_KEY: str = 'session_key'
    LAST_ACTIVITY: str = 'last_activity'
    USER_AGENT: str = 'user_agent'
    IP_ADRESS: str = 'ip'
    LAST_JWT_REFRESH: str = 'refresh_jwt'
    LAST_JWT_ACCESS: str = 'access_jwt'


# All the actions the client sends to the server
class RequestAction(str, Enum):
    # ── Matchmaking Actions ───────────────────────────────────────────────────────────
    JOIN_QUEUE: str = 'join_queue'
    LEAVE_QUEUE: str = 'leave_queue'
    LOCAL_GAME: str = 'local_game'

    # ── Duels ─────────────────────────────────────────────────────────────────────── #
    CREATE_DUEL: str = 'create_duel'
    LEAVE_DUEL: str = 'leave_duel'
    ACCEPT_DUEL: str = 'accept_duel'
    REFUSE_DUEL: str = 'refuse_duel'
    # ACK_ASK_DUEL: str = 'ack_ask_duel'

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
    START_TOURNAMENT: str = 'start_tournament'
    LIST_PLAYERS: str = 'list_players'
    TOURNAMENT_INFO: str = 'tournament_info'
    LIST_TOURNAMENT: str = 'list_tournament'
    GET_TOURNAMENT_CLIENTS: str = 'get_tournament_clients'
    INVITE_FRIEND: str = 'invite_friend'
    TOURNAMENT_INVITATION_RESPONSE: str = 'tournament_invitation_response'

    # ── Notification Actions ──────────────────────────────────────────────────────────────────
    SEND_FRIEND_REQUEST: str = "send_friend_request"
    ACCEPT_FRIEND_REQUEST: str = "accept_friend_request"
    REFUSE_FRIEND_REQUEST: str = "refuse_friend_request"
    DELETE_FRIEND: str = "delete_friend"
    BLOCK_FRIEND: str = "block_friend"
    UNBLOCK_FRIEND: str = "unblock_friend"
    BLOCK_UNBLOCK_FRIEND: str = "block_unblock_friend"
    GET_OPPONENT_NAME: str = "get_opponent_name"

    PING: str = 'ping'
    ONLINE_STATUS: str = "check_online_status"

# All the responses the server sends to the client
class ResponseAction(str, Enum):
    # ── Matchmaking Actions ───────────────────────────────────────────────────────────
    JOIN_QUEUE: str = 'You have successfully joined the queue'
    LEFT_QUEUE: str = 'You have successfully left the queue'

    # ── Duels ─────────────────────────────────────────────────────────────────────── #
    DUEL_CREATED: str = 'You have successfully create the duel'
    DUEL_JOIN: str = 'You have successfully joined the duel'
    DUEL_LEFT: str = 'You have successfully left the duel'
    ACK_ASK_DUEL: str = 'Response of asking to join a duel'
    ACK_PENDING_DUELS = 'Response of pending duels'
    REFUSED_DUEL: str = 'You have refused the duel.'
    DUEL_REFUSED: str = 'Duel refused'
    GET_OPPONENT: str = "get_opponent"

    # ── Tournaments ───────────────────────────────────────────────────────────────── #
    TOURNAMENT_CREATED: str = 'You have successfully create the tournament'
    TOURNAMENTS_NOTIFICATION: str = 'New tournaments created'
    TOURNAMENT_JOIN: str = 'You have successfully joined the tournament'
    TOURNAMENT_PLAYER_JOIN: str = 'Player join the tournament.'
    TOURNAMENT_PLAYER_LEFT: str = 'Player left the tournament.'
    TOURNAMENT_LEFT: str = 'You have successfully left the tournament'
    TOURNAMENT_WAITTING_PLAYERS: str = 'Waiting players for tournament'
    TOURNAMENT_PLAYERS_READY: str = 'Players are ready'
    TOURNAMENT_GAME_READY: str = 'Game is ready'
    TOURNAMENT_GAME_FINISH: str = 'Game is finished'
    TOURNAMENT_LOSE_GAME: str = "You're kick from tournament due to losing game."
    TOURNAMENT_CLOSING: str = 'Tournament close.'
    TOURNAMENT_PLAYERS_LIST: str = 'List of players'
    TOURNAMENT_INFO: str = 'Tournament info'
    TOURNAMENT_LIST: str = 'List of tournaments'
    TOURNAMENT_UPDATE: str = 'Tournament update'
    TOURNAMENT_STARTING: str = 'Tournament starting'
    WAITING_FOR_NEXT_ROUND: str = 'The tournament is waiting for the next round'

    # ── Game Actions ──────────────────────────────────────────────────────────────────
    JOIN_GAME: str = 'You have successfully joined the game'
    JOIN_LOCAL: str = 'You have successfully joined the local game'
    GAME_CREATED: str = 'You have successfully create the game'
    LEFT_GAME: str = 'You have successfully left the game'
    STARTING: str = 'The game is about to start'
    STARTED: str = 'The game has started'
    GAME_ENDING: str = 'The game has ended'
    WAITING_TO_START: str = 'Waiting for the game to start'

    # ── Update ────────────────────────────────────────────────────────────────────────
    PLAYER_INFOS: str = 'player_informations'
    BALL_UPDATE: str = 'ball_update'
    PADDLE_LEFT_UPDATE: str = 'paddle_left_update'
    PADDLE_RIGHT_UPDATE: str = 'paddle_right_update'
    SCORE_LEFT_UPDATE: str = 'score_left_update'
    SCORE_RIGHT_UPDATE: str = 'score_right_update'

    # ── Chat Actions ──────────────────────────────────────────────────────────────────
    ROOM_CREATED: str = "You have successfully created a chat room"
    MESSAGE_RECEIVED: str = "New message received"
    HISTORY_RECEIVED: str = "history_received"
    ALL_ROOM_RECEIVED: str = "all_room_received"
    NEW_FRIEND: str = "new_friend"
    ERROR_MESSAGE_USER_BLOCK: str = "error_message_user_block"
    
    # ── NOTIFICATION ACTION ───────────────────────────────────────────────────────────
    ACK_SEND_FRIEND_REQUEST: str = "acknowledge_send_friend_request"
    ACK_ACCEPT_FRIEND_REQUEST: str = "acknowledge_accept_friend_request"
    ACK_ACCEPT_FRIEND_REQUEST_HOST: str = "acknowledge_accept_friend_request_host"
    ACK_REFUSE_FRIEND_REQUEST: str = "acknowledge_refuse_friend_request"
    ACK_DELETE_FRIEND: str = "ack_delete_friend"
    ACK_DELETE_FRIEND_HOST: str = "ack_delete_friend_host"
    ACK_ONLINE_STATUS: str = "ack_online_status"
    FRIEND_BLOCKED: str = "friend_blocked"
    FRIEND_UNBLOCKED: str = "friend_unblocked"
    NOTIF_TEST = "notification_test"

    PONG: str = 'pong'
    TOURNAMENT_INVITATION = "TOURNAMENT_INVITATION"
    TOURNAMENT_INVITATION_SENT = "TOURNAMENT_INVITATION_SENT"
    TOURNAMENT_INVITATION_ACCEPTED = "TOURNAMENT_INVITATION_ACCEPTED"
    TOURNAMENT_INVITATION_REJECTED = "TOURNAMENT_INVITATION_REJECTED" 
    TOURNAMENT_INVITATION_ACCEPTED_BY = "TOURNAMENT_INVITATION_ACCEPTED_BY"
    TOURNAMENT_INVITATION_REJECTED_BY = "TOURNAMENT_INVITATION_REJECTED_BY"


# All the error messages sent to the client
class ResponseError(str, Enum):
    # ── Matchmaking ───────────────────────────────────────────────────────────────────
    ALREADY_IN_QUEUE: str = 'You are already on a queue.'
    ALREAY_IN_GAME: str = 'You are already in game.'
    NOT_IN_QUEUE: str = 'You are not currently in the queue.'
    MATCHMAKING_ERROR: str = 'Leaving matchmaking due to an error.'
    ALREADY_CONNECTED: str = 'You are already connected.'

    # ── Duels ─────────────────────────────────────────────────────────────────────── #
    DUEL_HIMSELF: str = 'You cannot duel yourself.'
    ALREADY_INVITED: str = 'You create a duel with a customer who has already invited you.'
    DUEL_NOT_EXIST: str = 'Duel you try to join not exist.'
    NOT_INVITED: str = 'You are not invited to this duel.'
    ALREADY_JOIN_DUEL: str = 'You try to join duel already joined.'
    CANNOT_REFUSE_DUEL: str = "You can't refuse a duel you already joined."
    BLOCKED_USER: str = 'You cannot duel a blocked user.'

    # ── Tournaments ───────────────────────────────────────────────────────────────── #
    KEY_ERROR: str = 'Error in tournament key.'
    TOURNAMENT_NOT_CREATE: str = 'There is error when you try to create tournaments.'
    TOURNAMENT_NOT_EXIST: str = 'Tournament you try to join not exist.'
    TOURNAMENT_FULL: str = 'Tournament is full'
    ALREADY_JOIN_TOURNAMENT: str = 'You try to join tournament already joined.'
    HOST_LEAVE: str = 'Host leave tournament.'
    NOT_IN_TOURNAMENT: str = "You're not in this tournament"
    INVITATION_NOT_FOUND: str = "Tournament invitation not found"
    INVITATION_ALREADY_SENT: str = "Tournament invitation already sent"

    # ── Game ──────────────────────────────────────────────────────────────────────────
    GAME_FULL: str = 'The game is currently full.'
    ALREADY_JOINED: str = "You have already joined the game."
    ALREADY_START: str = 'The game has already started.'
    JOINING_ERROR: str = 'Error occurred while trying to join.'
    OPPONENT_LEFT: str = 'Your opponent has left the game.'
    NOT_READY_TO_START: str = 'The game is not ready to start yet.'
    NO_GAME: str = 'There is no active game.'

    # ── Chat ──────────────────────────────────────────────────────────────────────────
    NO_HISTORY: str = 'There are no messages in this room.'
    ROOM_NOT_FOUND: str = 'Room does not exist.'
    NOT_ALLOWED: str = 'You are not allowed to send message.'
    SAME_ID: str = 'You can\'t create room with yourself.'

    # ── Notification ──────────────────────────────────────────────────────────────────────────
    USER_NOT_FOUND: str = 'User not found.'
    USER_ALREADY_MY_FRIEND: str = 'User already my friend.'
    USER_ALREADY_FRIEND_OR_NOT_PENDING_FRIEND: str = 'User already friend or not in pending list.'
    NOT_FRIEND: str = "not_friend"
    INTERNAL_ERROR: str = "internal_error"

    # ── Errors ────────────────────────────────────────────────────────────────────────
    CLIENT_NOT_FOUND: str = 'Your client ID does not correspond to a client.'
    JSON_ERROR: str = 'There is an error in JSON decoding.'
    EXCEPTION: str = 'An error has occurred.'
    SERVICE_ERROR: str = 'An error occurred in the service.'
    TARGET_NOT_FOUND: str = 'Target not found.'
    USER_OFFLINE: str = 'User is offline.'
    OPPONENT_NOT_FOUND: str = 'opponent_not_found'
    SESSION_EXPIRED: str = 'Session expired.'
    
    # INTERNAL_ERROR = "Internal server error"
    # INVALID_ID: str = 'Player does not exist'
    # NOT_READY: str = 'Players are not ready'
    # NOT_IN_GAME: str = 'Player is not in the game'


class RTables(str, Enum):
    # ── Groups ────────────────────────────────────────────────────────────────────── #
    GROUP_ERROR: str = 'error'
    GROUP_CLIENT: str = 'client_{}'
    GROUP_CHAT: str = 'chat_{}'
    GROUP_GAME: str = 'game_{}'
    GROUP_NOTIF: str = 'notification_{}'
    GROUP_TOURNAMENT: str = 'tournament_{}'

    # ── Hash Tables ───────────────────────────────────────────────────────────────── #
    HASH_CLIENT: str = 'client_{}'
    HASH_CLIENT_SESSION: str = 'client_session_{}'
    HASH_MATCHES: str = 'current_matches'
    HASH_TOURNAMENT_INVITATION = "tournament_invitation"
    # Queues
    HASH_QUEUE: str = 'queue_{}'
    HASH_G_QUEUE: str = HASH_QUEUE.format('global')
    HASH_DUEL_QUEUE: str = HASH_QUEUE.format("duel_{}")
    HASH_LOCAL_QUEUE: str = HASH_QUEUE.format("local")
    HASH_TOURNAMENT_QUEUE: str = HASH_QUEUE.format("tournament_{}")

    # ── Json ──────────────────────────────────────────────────────────────────────── #
    JSON_GAME: str = 'game_{}'
    JSON_DUEL: str = 'duel_{}'
    JSON_TOURNAMENT: str = 'tournament_{}'

    def __str__(self, *args) -> str:
        if '{}' in self.value:  # Si la chaîne contient un placeholder
            raise ValueError(
                f"L'élément '{self.name}' nécessite des arguments."
            )
        return str(self.value)

    def __call__(self, *args, **kwargs) -> str:
        return str(self.value.format(str(*args), **kwargs))


class PlayerSide(str, Enum):
    LEFT: str = 'player_left'
    RIGHT: str = 'player_right'

class PaddleMove(str, Enum):
    UP: str = 'up'
    DOWN: str = 'down'
    IDLE: str = 'idle'

class Ranks(str, Enum):
    BRONZE: str = 'bronze'
    SILVER: str = 'silver'
    GOLD: str = 'gold'
    DIAMOND: str = 'diamond'


class RanksThreshold(int, Enum):
    BRONZE = 0
    SILVER = 100
    GOLD = 200
    DIAMOND = 300

class JWTType(str, Enum):
    ACCESS: str = 'access'
    REFRESH: str = 'refresh'
