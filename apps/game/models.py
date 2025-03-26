import traceback

from django.db import models
from django.db.models import IntegerField, ForeignKey
from django.db.models.fields import DateTimeField
from django.utils import timezone
from redis import DataError
from redis.commands.json.path import Path

from apps.player.models import Player
from apps.shared.models import Clients
from apps.tournaments.models import Tournaments
from utils.pong.enums import GameStatus
from utils.redis import RedisConnectionPool
from utils.util import create_game_id


class Game(models.Model):
    class Meta:
        db_table = 'pong_games'

    # ═══════════════════════════════ Database Fields ════════════════════════════════ #

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    pk = IntegerField(primary_key=True, editable=False, null=False, unique=True)

    # ━━ Game informations ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    winner = ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='winner', blank=True)
    loser = ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='loser', blank=True)
    tournament_id = ForeignKey(Tournaments, on_delete=models.SET_NULL,
                               null=True, related_name='tournament', blank=True)
    created_at = DateTimeField(default=timezone.now)

    # ━━ Game setings ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    points_to_win = IntegerField(default=3)

    # ═════════════════════════════════ Local Fields ═════════════════════════════════ #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = RedisConnectionPool.get_sync_connection()
        self.id = create_game_id()
        self.game_key = f'game:{self.id}'
        self.pL: Player = None
        self.pR: Player = None
        print(self)

    def __str__(self):
        return f'Game with id: {self.id}'

    # ━━ GETTER / SETTER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ── Setter ────────────────────────────────────────────────────────────────────── #

    def rset_status(self, status: GameStatus):
        if self.rget_status() != status:
            self.redis.json().set(self.game_key, Path('status'), status.value)

    def rset_player(self, player: Player):
        pass

    # ── Getter ────────────────────────────────────────────────────────────────────── #

    def rget_status(self) -> GameStatus | None:
        try:
            status = self.redis.json().get(self.game_key, Path('status'))
            if status:
                return GameStatus(status)
            else:
                return None
        except DataError:
            traceback.print_exc()
            return None