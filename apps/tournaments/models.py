from datetime import timedelta

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import IntegerField, DateTimeField, \
    CharField, DurationField, JSONField, ForeignKey, TextField, BooleanField
from django.utils import timezone

from apps.client.models import Clients
from apps.player.models import Player
from utils.enums import TournamentStatus, RTables
from utils.redis import RedisConnectionPool
from utils.util import create_tournament_id, validate_even


#       serializer = ClientSerializer(data=request.data)
#       if serializer.is_valid():
#        Create your models here.

class Tournaments(models.Model):
    class Meta:
        db_table = 'pong_tournaments'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ PRIMARY FIEDLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = CharField(primary_key=True, editable=False, null=False, default=create_tournament_id, unique=True, max_length=5)

    # ── Tournaments Informations ───────────────────────────────────────────────────────────── #
    created_at = DateTimeField(default=timezone.now()) #I think its () at the end.
    status = CharField(max_length=20, choices=[(status.name, status.value) for status in TournamentStatus], default=TournamentStatus.CREATING.value)

    # ── Settings Of Tournaments ───────────────────────────────────────────────────── #
    name = TextField(max_length=30, null=False, default=f"{id}'s tournaments")
    host = ForeignKey(Clients, on_delete=models.SET_NULL, null=True)
    max_players = IntegerField(default=8, validators=[validate_even])
    players = models.ManyToManyField(Clients, related_name='tournaments_players', blank=True)
    scoreboards = JSONField(default=list)
    public = BooleanField(default=True)
    bots = BooleanField(default=False)

    # ── Game Tournament Settings ──────────────────────────────────────────────────── #
    timer = DurationField(default=timedelta(minutes=0), editable=False, null=True)
    points_to_win = IntegerField(default=11)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ SURCHARGE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __str__(self):
        return f"{self.name}, create by {self.host.profile.username}."


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    @staticmethod
    @sync_to_async
    def aget_tournament_by_id(code):
        try:
            with transaction.atomic():
                return Tournaments.objects.get(id=code)
        except Tournaments.DoesNotExist:
            return None
        except ValidationError:
            return None
