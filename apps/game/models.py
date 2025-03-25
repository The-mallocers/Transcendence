from datetime import timedelta

from django.db import models
from django.db.models import IntegerField, ForeignKey, CharField, \
    ManyToManyField
from django.db.models.fields import BooleanField, DurationField, DateTimeField
from django.utils import timezone

from apps.player.models import Player, PlayerGame
from apps.shared.models import Clients
from utils.pong.enums import GameStatus
from utils.util import create_game_id


class Game(models.Model):
    class Meta:
        db_table = 'pong_games'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ PRIMARY FIEDLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = IntegerField(primary_key=True, editable=False, null=False,
                      default=create_game_id, unique=True)

    # ── Game Informations ───────────────────────────────────────────────────────────── #
    created_at = DateTimeField(default=timezone.now)
    in_tournament = BooleanField(editable=False, default=False, null=False)
    points_to_win = IntegerField(default=3)
    winner = ForeignKey(Player, on_delete=models.SET_NULL, null=True,
                        related_name='winner', blank=True)
    loser = ForeignKey(Player, on_delete=models.SET_NULL, null=True,
                       related_name='loser', blank=True)
    
    winner_score = IntegerField(default=0)
    loser_score = IntegerField(default=0)
    
    # ── Game Settings ───────────────────────────────────────────────────────────── #
    status = CharField(max_length=20, choices=[(status.name, status.value) for status in GameStatus], default=GameStatus.CREATING.value)
    players = ManyToManyField(Player, through='player.PlayerGame')
    timer = DurationField(default=timedelta(minutes=0), editable=False, null=True) #In default there is no timer

    
