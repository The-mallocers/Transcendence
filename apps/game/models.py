from datetime import timedelta
import traceback

from django.db import models
from django.db.models import IntegerField, ForeignKey, CharField, \
    ManyToManyField
from django.db.models.fields import BooleanField, DurationField, DateTimeField
from django.utils import timezone

from apps.player.models import Player, PlayerGame
from apps.tournaments.models import Tournaments
from apps.shared.models import Clients
from utils.pong.enums import GameStatus
from utils.util import create_game_id
from utils.redis import RedisConnectionPool
from redis.commands.json.path import Path
from redis import DataError


class Game(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ PYTHON FIEDLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
        self.redis = RedisConnectionPool.get_sync_connection()
        self.pl: Player = None
        self.pr: Player = None
        self.id = None

    class Meta:
        db_table = 'pong_games'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ MODELS FIEDLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    pk = IntegerField(primary_key=True, editable=False, null=False,
                      default=create_game_id, unique=True)

    # ── Game Informations ───────────────────────────────────────────────────────────── #
    winner = ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='winner', blank=True)
    loser = ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='loser', blank=True)
    created_at = DateTimeField(default=timezone.now)
    tournament_id = ForeignKey(Tournaments, on_delete=models.SET_NULL, null=True, related_name='tournament', blank=True)
    
    # ── Game Settings ───────────────────────────────────────────────────────────── #
    points_to_win = IntegerField(default=3)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ METHODS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    
    # ── Setter ────────────────────────────────────────────────────────────────────────
    
    def rset_status(self, status: GameStatus):
        if self.rget_status() != status:
            self._redis.json().set(self.game_key, Path('status'), status.value)

    def rset_player(self, player: Player):
        pass

    # ── Getter ────────────────────────────────────────────────────────────────────────

    def rget_status(self) -> GameStatus | None:
        try:
            status = self._redis.json().get(self.game_key, Path('status'))
            if status:
                return GameStatus(status)
            else:
                return None
        except DataError:
            traceback.print_exc()
            return None