import json

from django.db import models, transaction
from django.db.models import ForeignKey, BigAutoField
from django.db.models.fields import IntegerField

from utils.enums import PlayerSide, RTables
from utils.redis import RedisConnectionPool


class PlayerRuntime:
    def __init__(self):
        from apps.client.models import Clients
        self.redis = None

        # ── Properties ───────────────────────────────────────────────────────────────── #
        self._client: Clients = None
        self._score = None

    # ═══════════════════════════════════ Properties ═══════════════════════════════════ #

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score

    # ════════════════════════════════════ Functions ════════════════════════════════════ #

    @classmethod
    def create_player(cls, client=None) -> 'Player':
        if cls is PlayerRuntime:
            player = PlayerRuntime()
        else:
            player = cls()

        player.client = client
        player.redis = RedisConnectionPool.get_sync_connection(player.__class__.__name__)
        return player

    def leave_queue(self, game_id, is_duel):
        if is_duel is True:
            self.redis.hdel(RTables.HASH_DUEL_QUEUE(game_id), str(self.client.id))
        if is_duel is False:
            self.redis.hdel(RTables.HASH_G_QUEUE, str(self.client.id))

    # ── Getter ────────────────────────────────────────────────────────────────────── #

    @staticmethod
    def get_player_side(client_id, game_key, redis):
        if redis is None:
            return None
        game_state_str = redis.json().get(game_key)

        # Parse the JSON string if it's a string
        if isinstance(game_state_str, str):
            game_state = json.loads(game_state_str)
        else:
            game_state = game_state_str

        # Ensure game_state is a list
        if not isinstance(game_state, list):
            game_state = [game_state]

        # Iterate through the game state
        for game in game_state:
            # Check player_left
            if game.get(PlayerSide.LEFT, {}).get('id') == str(client_id):
                return 'left'

            # Check player_right
            if game.get(PlayerSide.RIGHT, {}).get('id') == str(client_id):
                return 'right'

        # Return None if player not found
        return None

class Player(models.Model, PlayerRuntime):
    class Meta:
        db_table = 'pong_players'

    # ═══════════════════════════════ Database Fields ════════════════════════════════ #
    id = BigAutoField(primary_key=True, editable=False, null=False)

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    game = ForeignKey('game.Game', on_delete=models.SET_NULL, null=True)
    client = ForeignKey('client.Clients', on_delete=models.SET_NULL, null=True)

    # ━━ PLAYER INFOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    score = IntegerField(default=0)
    mmr_change = IntegerField(default=0)

    def __str__(self):
        if self._client is not None:
            return f'Runtime Player with client id: {self._client.id}'
        elif self.client is not None:
            return f'Database Player {self.id} with client id: {self.client.id}'
        else:
            return 'Uninitialized Player'

    def __init__(self, *args, **kwargs):
        PlayerRuntime.__init__(self)
        models.Model.__init__(self, *args, **kwargs)

    # ═══════════════════════════════════ Functions ════════════════════════════════════ #

    def save(self, *args, **kwargs):
        if self._client is not None:
            self.client = self._client
        if self._score is not None:
            self.score = self._score
        super().save(*args, **kwargs)

    @staticmethod
    def get_player_by_client(client_id):
        from apps.client.models import Clients
        try:
            with transaction.atomic():
                return Player.objects.get(client__id=client_id)
        except Clients.DoesNotExist:
            return None

    @staticmethod
    def get_player_by_id(player_id) -> 'Player':
        try:
            with transaction.atomic():
                return Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return None
