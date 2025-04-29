from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import IntegerField, ForeignKey, CharField, ImageField
from django.db.models.fields import DateTimeField, BooleanField
from django.utils import timezone
from redis import DataError
from redis.commands.json.path import Path

from apps.client.models import Clients
from apps.player.models import Player
from apps.tournaments.models import Tournaments
from utils.enums import EventType, ResponseAction, Ranks, RTables, PlayerSide
from utils.enums import GameStatus
from utils.redis import RedisConnectionPool
from utils.serializers.player import PlayersRedisSerializer
from utils.util import create_game_id
from utils.websockets.channel_send import send_group


class Rank(models.Model):
    class Meta:
        db_table = 'pong_ranks'

    name = CharField(primary_key=True, max_length=15, editable=False, null=False,
                     choices=[(ranks.name, ranks.value) for ranks in Ranks])
    icon = ImageField(upload_to='rank_icon/', null=False)
    mmr_min = IntegerField(null=False)
    mmr_max = IntegerField(null=False)


class Game(models.Model):
    class Meta:
        db_table = 'pong_games'

    # ═══════════════════════════════ Database Fields ════════════════════════════════ #

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = CharField(primary_key=True, editable=False, null=False, unique=True, max_length=5)

    # ━━ Game informations ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    winner = ForeignKey(Player, on_delete=models.SET_NULL, related_name='winner', null=True)
    loser = ForeignKey(Player, on_delete=models.SET_NULL, related_name='loser', null=True)
    tournament_id = ForeignKey(Tournaments, on_delete=models.SET_NULL,
                               null=True, related_name='tournament', blank=True)
    created_at = DateTimeField(default=timezone.now)
    is_duel = BooleanField(default=False)

    # ━━ Game setings ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    points_to_win = IntegerField(default=3)

    # ═════════════════════════════════ Local Fields ═════════════════════════════════ #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = create_game_id()
        self.redis = RedisConnectionPool.get_sync_connection(self.__class__.__name__ + f'_{self.code}')
        self.game_key = RTables.JSON_GAME(self.code)
        self.tournament_code = None
        self.pL: Player = None
        self.pR: Player = None

    def __str__(self):
        return f'Game with id: {self.code}'

    def create_redis_game(self):
        from utils.serializers.game import GameSerializer
        serializer = GameSerializer(self, context={'id': self.code, 'is_duel': self.is_duel})
        self.redis.json().set(self.game_key, Path.root_path(), serializer.data)

    def init_players(self):
        # On ajoute a la db de redis , a l'id de la game, les infos des deux joueurs
        players_serializer = PlayersRedisSerializer(instance={PlayerSide.LEFT: self.pL, PlayerSide.RIGHT: self.pR})
        existing_data = self.redis.json().get(self.game_key)
        existing_data.update(players_serializer.data)
        self.redis.json().set(self.game_key, Path.root_path(), existing_data)

        self.redis.hset(name=RTables.HASH_MATCHES, key=str(self.pL.client_id), value=str(self.code))
        self.redis.hset(name=RTables.HASH_MATCHES, key=str(self.pR.client_id), value=str(self.code))

        if self.tournament_code is None:  # si la game n'est pas dans un tournois
            channel_layer = get_channel_layer()

            channel_name_pL = self.redis.hget(name=RTables.HASH_CLIENT(self.pL.client_id), key=str(EventType.GAME.value))
            channel_name_pR = self.redis.hget(name=RTables.HASH_CLIENT(self.pR.client_id), key=str(EventType.GAME.value))
            async_to_sync(channel_layer.group_add)(RTables.GROUP_GAME(self.code), channel_name_pL)
            async_to_sync(channel_layer.group_add)(RTables.GROUP_GAME(self.code), channel_name_pR)

            self.pL.leave_queue(self.code, self.is_duel)
            self.pR.leave_queue(self.code, self.is_duel)

            send_group(RTables.GROUP_GAME(self.code), EventType.GAME, ResponseAction.JOIN_GAME)

    def error_game(self):
        self.rset_status(GameStatus.ERROR)
        self.redis.delete(self.game_key)

    # ━━ GETTER / SETTER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ── Setter ────────────────────────────────────────────────────────────────────── #

    def rset_status(self, status):
        if self.rget_status() != status:
            self.redis.json().set(self.game_key, Path('status'), status)

    # ── Getter ────────────────────────────────────────────────────────────────────── #

    def rget_status(self) -> GameStatus | None:
        try:
            status = self.redis.json().get(self.game_key, Path('status'))
            return GameStatus(status)
        except DataError:
            return None

    def rget_is_duel(self) -> bool | None:
        try:
            status = self.redis.json().get(self.game_key, Path('is_duel'))
            return bool(status)
        except DataError:
            return None
