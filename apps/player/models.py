import uuid

from channels.db import database_sync_to_async
from django.db import models
from django.db.models import ManyToManyField, ForeignKey, \
    OneToOneField
from django.db.models.fields import CharField, IntegerField, BooleanField, \
    DateTimeField
from django.utils import timezone

from utils.pong.enums import Side, Ranks


class Player(models.Model):
    class Meta:
        db_table = 'players_list'

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)

    # ━━ PLAYER INFOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    nickname = CharField(max_length=20, null=True, editable=False)
    stats = ForeignKey('player.PlayerStats', on_delete=models.CASCADE, null=True)
    # friends = ManyToManyField('self', symmetrical=False, blank=True, related_name='friends_with')
    # friends_requests = ManyToManyField('self', symmetrical=False, blank=True, related_name='invited_by')
    # friends_invitations = ManyToManyField('self', symmetrical=False, blank=True, related_name='requested_by')

    # ── Custom ──────────────────────────────────────────────────────────────────────── #
    skin_ball = CharField(max_length=100, null=True) #A voir quel field il faut mettre
    skin_paddle = CharField(max_length=100, null=True)



class PlayerGame(models.Model):
    class Meta:
        db_table = 'players_games'
        unique_together = ('player', 'game')

    # ── Links ─────────────────────────────────────────────────────────────────────────
    player = ForeignKey(Player, on_delete=models.CASCADE)
    game = ForeignKey('game.Game', on_delete=models.CASCADE)

    # ── Informations ──────────────────────────────────────────────────────────────────
    side = CharField(max_length=5, null=True, choices=[(side.name, side.value) for side in Side], default=None)
    score = IntegerField(default=0)
    joined_at = DateTimeField(default=timezone.now)
    is_ready = BooleanField(default=False)

    def __str__(self):
        return self.player.nickname



class PlayerStats(models.Model):
    class Meta:
        db_table = 'players_stats'

    # ── Informations ──────────────────────────────────────────────────────────────────
    total_game = IntegerField(default=0, blank=True)
    wins = IntegerField(default=0, blank=True)
    losses = IntegerField(default=0, blank=True)
    mmr = IntegerField(default=50, blank=True)
    rank = ForeignKey('pong.Rank', on_delete=models.SET_NULL, null=True, blank=True, default=Ranks.BRONZE.value)