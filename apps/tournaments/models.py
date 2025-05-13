from datetime import timedelta

from asgiref.sync import sync_to_async
from django.db import models
from django.db.models import IntegerField, DateTimeField, \
    CharField, DurationField, JSONField, ForeignKey, TextField, BooleanField
from django.utils import timezone

from apps.client.models import Clients
from apps.player.models import Player
from utils.enums import RTables, TournamentStatus
from utils.serializers.tournament import TournamentSerializer
from utils.util import create_tournament_id, validate_even
from redis.commands.json.path import Path


class TournamentRuntime:
    def __init__(self):
        self.serializer: TournamentSerializer = None
        # ── Properties ──────────────────────────────────────────────────────────────── #
        self._code: str = None
        self._status: TournamentStatus = None
        self._title: str = None
        self._host: Clients = None
        self._max_clients: int = None
        self._clients: list[Clients] = None
        self._is_public: bool = False
        self._has_bots: bool = False
        self._timer = None
        self._points_to_win: int = None

    # ═══════════════════════════════════ Properties ═══════════════════════════════════ #

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def status(self):
        return self._status

    @property
    def title(self):
        return self._title

    @property
    def host(self):
        return self._host

    @property
    def max_clients(self):
        return self._max_clients

    @property
    def clients(self):
        return self._clients

    @property
    def is_public(self):
        return self._is_public

    @property
    def has_bots(self):
        return self._has_bots

    @property
    def points_to_win(self):
        return self._points_to_win

    @property
    def timer(self):
        return self._timer

    @status.setter
    def status(self, value):
        self._status = value

    @host.setter
    def host(self, value):
        self._host = value

    @title.setter
    def title(self, value):
        self._title = value

    @max_clients.setter
    def max_clients(self, value):
        self._max_clients = value

    @is_public.setter
    def is_public(self, value):
        self._is_public = value

    @has_bots.setter
    def has_bots(self, value):
        self._has_bots = value

    @points_to_win.setter
    def points_to_win(self, value):
        self._points_to_win = value

    @timer.setter
    def timer(self, value):
        self._timer = value

    @clients.setter
    def clients(self, value):
        self._clients = value

    # ═══════════════════════════════════ Functions ════════════════════════════════════ #

    @classmethod
    async def create_tournament(cls, data, redis, runtime=False) -> 'Tournaments':
        if runtime or cls is TournamentRuntime:
            tournament = TournamentRuntime()
        else:
            tournament = await sync_to_async(cls)()

        tournament.serializer = TournamentSerializer(data=data)
        if tournament.serializer.is_valid():
            tournament.code = await sync_to_async(create_tournament_id)()
            tournament.status = TournamentStatus.CREATING
            tournament.host = await Clients.aget_client_by_id(data['host'])
            tournament.clients = [tournament.host]

            # ── Initialized With Data ─────────────────────────────────────────────────
            tournament.title = tournament.serializer.validated_data['title']
            tournament.max_clients = tournament.serializer.validated_data['max_clients']
            tournament.is_public = tournament.serializer.validated_data['is_public']
            tournament.has_bots = tournament.serializer.validated_data['has_bots']
            tournament.points_to_win = tournament.serializer.validated_data['points_to_win']
            tournament.timer = tournament.serializer.validated_data['timer']

            # ── Creating Tournament In Database ───────────────────────────────────────
            await Tournaments.objects.acreate(code=tournament.code, host=tournament.host, title=tournament.title,
                                              max_clients=tournament.max_clients, is_public=tournament.is_public, has_bots=tournament.has_bots,
                                              points_to_win=tournament.points_to_win, timer=timedelta(seconds=tournament.timer))
            await redis.json().set(RTables.JSON_TOURNAMENT(tournament.code), Path.root_path(), tournament.serializer.data) #Brand new moved line !
            return tournament
        else:
            for field, errors in tournament.serializer.errors.items():
                for error in errors:
                    raise ValueError(f'{field}: {error}')


class Tournaments(models.Model, TournamentRuntime):
    class Meta:
        db_table = 'pong_tournaments'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ PRIMARY FIEDLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    code = CharField(primary_key=True, editable=False, null=False, default='', unique=True, max_length=5)

    # ── Tournaments Informations ───────────────────────────────────────────────────────────── #
    created_at = DateTimeField(default=timezone.now)  # I think its () at the end.
    scoreboards = JSONField(default=list)

    # ── Settings Of Tournaments ───────────────────────────────────────────────────── #
    title = TextField(max_length=30, null=False, default=f"{code}'s tournaments")
    max_clients = IntegerField(default=8, validators=[validate_even])
    host = ForeignKey(Clients, on_delete=models.SET_NULL, null=True, related_name='host')
    winner = ForeignKey(Clients, on_delete=models.SET_NULL, null=True, blank=True, related_name='winner')
    clients = models.ManyToManyField(Clients, related_name='tournaments_players', blank=True)
    is_public = BooleanField(default=True)
    has_bots = BooleanField(default=False)

    # ── Game Tournament Settings ──────────────────────────────────────────────────── #
    timer = DurationField(default=timedelta(minutes=0), editable=False, null=True)
    points_to_win = IntegerField(default=11)

    def __str__(self):
        return f"{self.title}, create by {self.host.profile.username}."

    def __init__(self, *args, **kwargs):
        TournamentRuntime.__init__(self)
        models.Model.__init__(self, *args, **kwargs)

    # ═══════════════════════════════════ Functions ════════════════════════════════════ #

    def save(self, *args, **kwargs):
        if self._code is not None:
            self.code = self._code
        if self._status is not None:
            self.status = self._status
        if self._title is not None:
            self.title = self._title
        if self._max_clients is not None:
            self.max_clients = self._max_clients
        if self._clients is not None:
            self.clients.set(self._clients)
        if self._points_to_win is not None:
            self.points_to_win = self._points_to_win
        super().save(*args, **kwargs)

    @staticmethod
    def get_tournament_by_code(code):
        try:
            tournament = Tournaments.objects.get(code=code)
            return tournament
        except Tournaments.DoesNotExist:
            return None
