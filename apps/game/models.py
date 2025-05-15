from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import IntegerField, ForeignKey, CharField
from django.db.models.fields import DateTimeField, BooleanField
from django.utils import timezone
from redis import DataError
from redis.commands.json.path import Path

from apps.client.models import Clients
from apps.player.models import Player
from apps.tournaments.models import Tournaments
from utils.enums import EventType, ResponseAction, RTables, PlayerSide
from utils.enums import GameStatus
from utils.redis import RedisConnectionPool
from utils.serializers.player import PlayersRedisSerializer
from utils.util import create_game_id
from utils.websockets.channel_send import send_group


class GameRuntime:
    def __init__(self):
        self.redis = None
        self.game_key = None
        self.pL: Player = None
        self.pR: Player = None

        # ── Properties ───────────────────────────────────────────────────────────────── #
        self._code = None
        self._tournament: Tournaments = None
        self._is_duel = False
        self._points_to_win = 3

    # ═══════════════════════════════════ Properties ═══════════════════════════════════ #

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def tournament(self):
        return self._tournament

    @tournament.setter
    def tournament(self, value):
        self._tournament = value

    @property
    def is_duel(self):
        return self._is_duel

    @is_duel.setter
    def is_duel(self, value):
        self._is_duel = value

    @property
    def points_to_win(self):
        return self._points_to_win

    @points_to_win.setter
    def points_to_win(self, points):
        self._points_to_win = points

    # ════════════════════════════════════ Functions ════════════════════════════════════ #

    @classmethod
    def create_game(cls, tournament=None, runtime=False) -> 'Game':
        if runtime or cls is GameRuntime:
            game = GameRuntime()
        else:
            game = cls()

        game.code = create_game_id()
        game.game_key = RTables.JSON_GAME(game.code)
        game.tournament = tournament
        game.redis = RedisConnectionPool.get_sync_connection(game.__class__.__name__)
        return game

    def create_redis_game(self):
        from utils.serializers.game import GameSerializer
        if self.tournament is None:
            serializer = GameSerializer(self, context={'id': self.code, 'is_duel': self.is_duel})
        else:
            serializer = GameSerializer(self, context={'id': self.code, 'is_duel': self.is_duel, 'tournament_code': self.tournament.code})
        self.redis.json().set(self.game_key, Path.root_path(), serializer.data)

    def init_players(self):
        players_serializer = PlayersRedisSerializer(instance={PlayerSide.LEFT: self.pL, PlayerSide.RIGHT: self.pR})
        existing_data = self.redis.json().get(self.game_key)
        existing_data.update(players_serializer.data)
        self.redis.json().set(self.game_key, Path.root_path(), existing_data)

        self.redis.hset(name=RTables.HASH_MATCHES, key=str(self.pL.client.id), value=str(self.code))
        self.redis.hset(name=RTables.HASH_MATCHES, key=str(self.pR.client.id), value=str(self.code))

        #Update le JSON du tournoi.
        if self.tournament:
            print("bonjour je vais update le nom des joueurs !")
            from utils.threads.tournament import TournamentThread
            TournamentThread.set_game_players_name(self.tournament.code, self.code, self.pL, self.pR, self.redis)

        if self.tournament is None:  # si la game n'est pas dans un tournois
            channel_layer = get_channel_layer()

            channel_name_pL = self.redis.hget(name=RTables.HASH_CLIENT(self.pL.client.id), key=str(EventType.GAME.value))
            channel_name_pL = channel_name_pL.decode('utf-8')
            channel_name_pR = self.redis.hget(name=RTables.HASH_CLIENT(self.pR.client.id), key=str(EventType.GAME.value))
            channel_name_pR = channel_name_pR.decode('utf-8')
            async_to_sync(channel_layer.group_add)(RTables.GROUP_GAME(self.code), channel_name_pL)
            async_to_sync(channel_layer.group_add)(RTables.GROUP_GAME(self.code), channel_name_pR)

            self.pL.leave_queue(self.code, self.is_duel)
            self.pR.leave_queue(self.code, self.is_duel)

            send_group(RTables.GROUP_GAME(self.code), EventType.GAME, ResponseAction.JOIN_GAME)

    def error_game(self):
        self.rset_status(GameStatus.ERROR)
        self.redis.delete(self.game_key)

    # ── Setter ────────────────────────────────────────────────────────────────────── #

    def rset_status(self, status):
        if self.rget_status() != status:
            if self.tournament is not None:
                from utils.threads.tournament import TournamentThread
                TournamentThread.set_game_status(self.tournament.code, self.code, status, self.redis)
                #Send back to the client that an update happened, so they can ask for the new state.
                print("Sending back that i updated tournament state")
                send_group(RTables.GROUP_TOURNAMENT(self.tournament.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_UPDATE)
            self.redis.json().set(self.game_key, Path('status'), status)

    # ── Getter ────────────────────────────────────────────────────────────────────── #

    def rget_status(self) -> GameStatus | None:
        try:
            status = self.redis.json().get(self.game_key, Path('status'))
            return GameStatus(status)
        except ValueError:
            return None

    def rget_is_duel(self) -> bool | None:
        try:
            status = self.redis.json().get(self.game_key, Path('is_duel'))
            return bool(status)
        except DataError:
            return None

class Game(models.Model, GameRuntime):
    class Meta:
        db_table = 'pong_games'

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    code = CharField(primary_key=True, editable=False, null=False, unique=True, max_length=5, default='')

    # ━━ Game informations ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    winner = ForeignKey(Player, on_delete=models.SET_NULL, related_name='winner', null=True)
    loser = ForeignKey(Player, on_delete=models.SET_NULL, related_name='loser', null=True)
    tournament = ForeignKey(Tournaments, on_delete=models.SET_NULL, null=True, related_name='tournament', blank=True)
    created_at = DateTimeField(default=timezone.now)
    is_duel = BooleanField(default=False)
    points_to_win = IntegerField(default=3)

    def __str__(self):
        return f'Game with id: {self.code}'

    def __init__(self, *args, **kwargs):
        GameRuntime.__init__(self)
        models.Model.__init__(self, *args, **kwargs)

    # ═══════════════════════════════════ Functions ════════════════════════════════════ #

    def save(self, *args, **kwargs):
        if self._code is not None:
            self.code = self._code
        if self._tournament is not None:
            self.tournament = self._tournament
        if self._is_duel is not None:
            self.is_duel = self._is_duel
        if self._points_to_win is not None:
            self.points_to_win = self._points_to_win
        super().save(*args, **kwargs)

    @staticmethod
    def get_game_by_id(code) -> 'Game':
        try:
            game = Game.objects.get(code=code)
            return game
        except:
            return None