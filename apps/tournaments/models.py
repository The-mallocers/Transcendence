from datetime import timedelta

from django.db import models
from django.db.models import IntegerField, DateTimeField, \
    CharField, DurationField, JSONField
from django.utils import timezone

from utils.pong.enums import TournamentStatus
from utils.util import create_tournament_id, validate_even


# Create your models here.
class Tournaments(models.Model):
    class Meta:
        db_table = 'pong_tournaments'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ PRIMARY FIEDLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = IntegerField(primary_key=True, editable=False, null=False,
                      default=create_tournament_id, unique=True)

    # ── Tournaments Informations ───────────────────────────────────────────────────────────── #
    created_at = DateTimeField(default=timezone.now)
    status = CharField(max_length=20,
                       choices=[(status.name, status.value) for status in
                                TournamentStatus],
                       default=TournamentStatus.CREATING.value)
    timer = DurationField(default=timedelta(minutes=0), editable=False,
                          null=True)
    max_players = IntegerField(default=8, validators=[validate_even])
    # games = ManyToManyField('shared.Game', related_name='games')
    scoreboards = JSONField(default=list)
