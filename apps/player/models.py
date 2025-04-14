import json

from django.db import models, transaction
from django.db.models import ForeignKey
from django.db.models.fields import IntegerField

from utils.enums import PlayerSide, RTables
from utils.redis import RedisConnectionPool


class Player(models.Model):
    class Meta:
        db_table = 'pong_players'

    # ═══════════════════════════════ Database Fields ════════════════════════════════ #

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    game = ForeignKey('game.Game', on_delete=models.SET_NULL, null=True)
    client = ForeignKey('client.Clients', on_delete=models.SET_NULL, null=True)

    # ━━ PLAYER INFOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    score = IntegerField(default=0)

    # ═════════════════════════════════ Local Fields ═════════════════════════════════ #
    def __init__(self, client_id=None, *args, **kwargs):
        from apps.client.models import Clients
        super().__init__(*args, **kwargs)
        self.class_client = Clients.get_client_by_id(client_id)
        self.client_id = client_id
        self.redis = RedisConnectionPool.get_sync_connection(self.__class__.__name__)

    def __str__(self):
        return f'Player with client id: {self.client_id}'

    def leave_queue(self, game_id, is_duel):
        if is_duel is True:
            self.redis.hdel(RTables.HASH_DUEL_QUEUE(game_id), str(self.client_id))
        if is_duel is False:
            self.redis.hdel(RTables.HASH_G_QUEUE, str(self.client_id))

    # ━━ GETTER / SETTER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ── Setter ────────────────────────────────────────────────────────────────────── #

    # ── Getter ────────────────────────────────────────────────────────────────────── #
    @staticmethod
    def get_player_by_client(client_id):
        from apps.client.models import Clients
        try:
            with transaction.atomic():
                return Player.objects.get(client__id=client_id)
        except Clients.DoesNotExist:
            return None

    @staticmethod
    def get_player_side(player_id, game_key, redis):
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
            if game.get(PlayerSide.LEFT, {}).get('id') == player_id:
                return 'left'

            # Check player_right
            if game.get(PlayerSide.RIGHT, {}).get('id') == player_id:
                return 'right'

        # Return None if player not found
        return None
