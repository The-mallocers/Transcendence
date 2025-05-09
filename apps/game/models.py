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
from utils.enums import EventType, ResponseAction, RTables, PlayerSide
from utils.enums import GameStatus
from utils.redis import RedisConnectionPool
from utils.serializers.player import PlayersRedisSerializer
from utils.util import create_game_id
from utils.websockets.channel_send import send_group

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
        self.redis = RedisConnectionPool.get_sync_connection()
        self.code = create_game_id()
        self.game_key = RTables.JSON_GAME(self.code)
        self.pL: Player = None
        self.pR: Player = None

    def __str__(self):
        return f'Game with id: {self.code}'

    def create_redis_game(self):
        from utils.serializers.game import GameSerializer
        serializer = GameSerializer(self, context={'id': self.code, 'is_duel': self.is_duel})
        self.redis.json().set(self.game_key, Path.root_path(), serializer.data)

    def init_players(self):
        print(f"My player r is {self.pR}")
        print(f"My player l is {self.pL}")

        # On ajoute a la db de redis , a l'id de la game, les infos des deux joueurs
        players_serializer = PlayersRedisSerializer(instance={PlayerSide.LEFT: self.pL, PlayerSide.RIGHT: self.pR})
        existing_data = self.redis.json().get(self.game_key)
        existing_data.update(players_serializer.data)
        self.redis.json().set(self.game_key, Path.root_path(), existing_data)

        # getting channel layer
        channel_layer = get_channel_layer()
        print("We reached step 0")
        # Add two player in group of the new game
        channel_name_pL = self.redis.hget(name=RTables.HASH_CLIENT(self.pL.client_id), key=str(EventType.GAME.value))
        print("We reached step 0,1")
        async_to_sync(channel_layer.group_add)(RTables.GROUP_GAME(self.code), channel_name_pL)
        print("We reached step 0,2")
        channel_name_pR = self.redis.hget(name=RTables.HASH_CLIENT(self.pR.client_id), key=str(EventType.GAME.value))
        print("We reached step 0,3")
        print(f"Here are all of the variables passed into group add : {self.code}, {channel_name_pR}")
        async_to_sync(channel_layer.group_add)(RTables.GROUP_GAME(self.code), channel_name_pR) #Bonjour je fais tout crash
        print("We reached step 1")
        self.redis.hset(name=RTables.HASH_MATCHES, key=str(self.pL.client_id), value=str(self.code))
        self.redis.hset(name=RTables.HASH_MATCHES, key=str(self.pR.client_id), value=str(self.code))
        print("We reached step 2")
        self.pL.leave_queue(self.code, self.is_duel)
        self.pR.leave_queue(self.code, self.is_duel)

        send_group(RTables.GROUP_GAME(self.code), EventType.GAME, ResponseAction.JOIN_GAME)
        print("We reached the end of init_players !")

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
