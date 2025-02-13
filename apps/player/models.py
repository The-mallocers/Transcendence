import uuid

from channels.db import database_sync_to_async
from django.db import models
from django.db.models import ManyToManyField, ForeignKey, \
    OneToOneField
from django.db.models.fields import CharField, IntegerField, BooleanField, \
    DateTimeField
from django.utils import timezone

from utils.pong.enums import Side


class Player(models.Model):
    class Meta:
        db_table = 'players_list'

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)

    # ━━ PLAYER INFOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    nickname = CharField(max_length=20, null=True, editable=False)
    friends = ManyToManyField('self', symmetrical=False, blank=True, related_name='friends_with')
    friends_requests = ManyToManyField('self', symmetrical=False, blank=True, related_name='invited_by')
    friends_invitations = ManyToManyField('self', symmetrical=False, blank=True, related_name='requested_by')

    # ── Custom ──────────────────────────────────────────────────────────────────────── #
    skin_ball = CharField(max_length=100, null=True) #A voir quel field il faut mettre
    skin_paddle = CharField(max_length=100, null=True)

    @staticmethod
    @database_sync_to_async
    def get(player_id):
        try:
            return Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return None

class PlayerGame(models.Model):
    class Meta:
        db_table = 'player_game'
        unique_together = ('player', 'game')

    # ── Links ─────────────────────────────────────────────────────────────────────────
    player = ForeignKey(Player, on_delete=models.CASCADE)
    game = ForeignKey('game.Game', on_delete=models.CASCADE)

    # ── Informations ──────────────────────────────────────────────────────────────────
    side = CharField(max_length=5, null=True, choices=[(side.name, side.value) for side in Side], default=None)
    score = IntegerField(default=0)
    joined_at = DateTimeField(default=timezone.now)
    is_ready = BooleanField(default=False)

class PlayerStats(models.Model):
    class Meta:
        db_table = 'player_stats'

    # ── Links ─────────────────────────────────────────────────────────────────────────
    player = OneToOneField(Player, on_delete=models.CASCADE)

    # ── Informations ──────────────────────────────────────────────────────────────────
    total_game = IntegerField(default=0)
    wins = IntegerField(default=0)
    losses = IntegerField(default=0)
    mmr = IntegerField(default=100, blank=True)
    rank = ForeignKey('pong.Rank', on_delete=models.SET_NULL, null=True, blank=True)