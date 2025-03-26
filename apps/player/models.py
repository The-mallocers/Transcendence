from django.db import models, transaction
from django.db.models import ForeignKey
from django.db.models.fields import IntegerField, CharField

from utils.pong.enums import Ranks
from utils.redis import RedisConnectionPool


class Player(models.Model):
    class Meta:
        db_table = 'pong_players'

    # ═══════════════════════════════ Database Fields ════════════════════════════════ #

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    game = ForeignKey('game.Game', on_delete=models.SET_NULL, null=True)
    client = ForeignKey('shared.Clients', on_delete=models.CASCADE, null=False)

    # ━━ PLAYER INFOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    score = IntegerField(default=0)

    # ═════════════════════════════════ Local Fields ═════════════════════════════════ #
    def __init__(self, client_id, *args, **kwargs):
        from apps.shared.models import Clients
        super().__init__(*args, **kwargs)
        self.class_client = Clients.get_client_by_id(client_id)
        self.redis = RedisConnectionPool.get_sync_connection(self.__class__.__name__)

    def __str__(self):
        return f'Player with client id: {self.class_client.id}'
    
    def leave_queue(self):
        self.redis.hdel('matchmaking_queue', str(self.class_client.id))

    # ━━ GETTER / SETTER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ── Setter ────────────────────────────────────────────────────────────────────── #

    # ── Getter ────────────────────────────────────────────────────────────────────── #
    @staticmethod
    def get_player_by_client(client_id):
        from apps.shared.models import Clients
        try:
            with transaction.atomic():
                return Player.objects.get(client__id=client_id)
        except Clients.DoesNotExist:
            return None



class PlayerStats(models.Model):
    class Meta:
        db_table = 'players_stats'

    # ── Informations ──────────────────────────────────────────────────────────────────
    total_game = IntegerField(default=0, blank=True)
    wins = IntegerField(default=0, blank=True)
    losses = IntegerField(default=0, blank=True)
    mmr = IntegerField(default=50, blank=True)
    # rank = ForeignKey('pong.Rank', on_delete=models.SET_NULL, null=True, blank=True, default=Ranks.BRONZE.value)
    rank = CharField(default=Ranks.BRONZE.value, max_length=100, blank=True)
    #I am like so sure this doesnt work because it doesnt know where pong.rank is