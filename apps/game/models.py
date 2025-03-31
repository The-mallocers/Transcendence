import traceback

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import IntegerField, ForeignKey, CharField, ImageField
from django.db.models.fields import DateTimeField
from django.utils import timezone
from redis import DataError
from redis.commands.json.path import Path

from apps.player.models import Player
from apps.tournaments.models import Tournaments
from utils.enums import EventType, ResponseAction, Ranks
from utils.enums import GameStatus
from utils.redis import RedisConnectionPool
from utils.serializers.player import PlayersRedisSerializer
from utils.util import create_game_id
from utils.websockets.channel_send import send_group


class Rank(models.Model):
    class Meta:
        db_table = 'ranks_list'

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
    id = IntegerField(primary_key=True, editable=False, null=False, unique=True)

    # ━━ Game informations ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    winner = ForeignKey(Player, on_delete=models.SET_NULL, related_name='winner', null=True)
    loser = ForeignKey(Player, on_delete=models.SET_NULL, related_name='loser', null=True)
    tournament_id = ForeignKey(Tournaments, on_delete=models.SET_NULL,
                               null=True, related_name='tournament', blank=True)
    created_at = DateTimeField(default=timezone.now)

    # ━━ Game setings ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    points_to_win = IntegerField(default=3)

    # ═════════════════════════════════ Local Fields ═════════════════════════════════ #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = RedisConnectionPool.get_sync_connection()
        self.game_id = create_game_id()
        self.game_key = f'game:{self.game_id}'
        self.pL: Player = None
        self.pR: Player = None

    def __str__(self):
        return f'Game with id: {self.game_id}'

    def create_redis_game(self):
        from utils.serializers.game import GameSerializer
        serializer = GameSerializer(self, context={'id': self.game_id})
        self.redis.json().set(self.game_key, Path.root_path(), serializer.data)

    def init_players(self):
        # On ajoute a la db de redis , a l'id de la game, les infos des deux joueurs
        players_serializer = PlayersRedisSerializer(instance={'player_left': self.pL, 'player_right': self.pR})
        existing_data = self.redis.json().get(self.game_key)
        existing_data.update(players_serializer.data)
        self.redis.json().set(self.game_key, Path.root_path(), existing_data)

        # getting channel layer
        channel_layer = get_channel_layer()

        # Add two player in group of the new game
        channel_name_pL = self.redis.hget(name="consumers_channels", key=str(self.pL.client_id))
        async_to_sync(channel_layer.group_add)(str(self.game_id), channel_name_pL)
        channel_name_pR = self.redis.hget(name="consumers_channels", key=str(self.pR.client_id))
        async_to_sync(channel_layer.group_add)(str(self.game_id), channel_name_pR)

        # Add the players in player_game redis table
        self.redis.hset(name="current_matches", key=str(self.pL.client_id), value=str(self.game_id))
        self.redis.hset(name="current_matches", key=str(self.pR.client_id), value=str(self.game_id))

        self.pL.leave_queue()
        self.pR.leave_queue()

        send_group(self.game_id, EventType.GAME, ResponseAction.JOIN_GAME)

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
            if status:
                return GameStatus(status)
            else:
                return None
        except DataError:
            traceback.print_exc()
            return None
