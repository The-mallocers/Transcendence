import random
import traceback

from django.db import models
from django.db.models import IntegerField, ForeignKey
from django.db.models.fields import DateTimeField
from django.utils import timezone
from redis import DataError
from redis.commands.json.path import Path

from apps.player.api.serializers import PlayersRedisSerializer
from apps.player.models import Player
from apps.game.api.serializers import GameSerializer
from apps.shared.models import Clients
from apps.tournaments.models import Tournaments
from utils.pong.enums import GameStatus, ResponseAction, Side
from utils.redis import RedisConnectionPool
from utils.util import create_game_id
from channels.layers import get_channel_layer
from utils.websockets.channel_send import send_group
from utils.pong.enums import EventType, ResponseAction

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
    
    def create_redis_game(self):
        serializer = GameSerializer(self)
        self.redis.json().set(self.game_key, Path.root_path(), serializer.data)

    def init_players(self):
        #On ajoute a la db de redis , a l'id de la game, les infos des deux joueurs
        players_serializer = PlayersRedisSerializer({'player_left': self.pL, 'player_right': self.pR})
        self.redis.json().arrappend(self.id, Path("players"), players_serializer.data) 

        #getting channel layer
        channel_layer = get_channel_layer()

        channel_name_pL = self.redis.hget(name="consumers_channels", key=str(self.pL.class_client.id))
        channel_layer.group_add(str(self.id), channel_name_pL.decode('utf-8'))
        channel_name_pR = self.redis.hget(name="consumers_channels", key=str(self.pR.class_client.id))
        channel_layer.group_add(str(self.id), channel_name_pR.decode('utf-8'))

        self.pL.leave_queue()
        self.pR.leave_queue()

        send_group(self.id, EventType.GAME, ResponseAction.JOIN_GAME)

    def error_game(self):
        self.rset_status(GameStatus.ERROR)
        self.redis.delete(self.game_key)

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