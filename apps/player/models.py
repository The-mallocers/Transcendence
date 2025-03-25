import random
import uuid

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.db import models, transaction
from django.db.models import ManyToManyField, ForeignKey, \
    OneToOneField
from django.db.models.fields import CharField, IntegerField, BooleanField, \
    DateTimeField
from django.utils import timezone

from utils.pong.enums import ResponseError, Side, Ranks
from apps.shared.models import Clients
from utils.redis import RedisConnectionPool
from redis.commands.json.path import Path

from utils.websockets.channel_send import send_group_error


class Player(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = RedisConnectionPool.get_sync_connection(self.__class__.__name__)

    class Meta:
        db_table = 'pong_players'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ MODELS FIEDLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    game = ForeignKey('game.Game', on_delete=models.SET_NULL, null=False)
    client = ForeignKey(Clients, on_delete=models.CASCADE, null=False)

    # ━━ PLAYER INFOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    score = IntegerField(default=0)


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ METHODS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def join_game(self, game):
        #We will only want to join with Redis, not add to DB.
        try:
            game_key = f'game:{game.id}'
            players = self.redis.json().get(game_key, Path("players"))
            player_ids = [player["id"] for player in players]

            #This is just to find a side.
            if self.player.id in player_ids:
                return send_group_error(self.player.id, ResponseError.ALREADY_JOINED)
            else:
                if len(player_ids) == 0:
                    rand_side = random.choice(list(Side))
                    self._player_game.side = rand_side
                elif len(player_ids) == 1:
                    first_player: PlayerGame = await self.get_player_game_id_db_async(str(player_ids[0]), game_manager.get_id())
                    if first_player.side == Side.RIGHT.value:
                        self._player_game.side = Side.LEFT
                    if first_player.side == Side.LEFT.value:
                        self._player_game.side = Side.RIGHT
                elif len(player_ids) == 2:
                    return send_group_error(self.player.id, ResponseError.GAME_FULL)

            # ── Send Reponse To Player ────────────────────────────────────────────────
            #this wont really change.
            self.paddle.game_key = game_key
            serializer = PlayerSerializer(self.player,
                                          context={'paddle': self.paddle, 'side': self._player_game.side, 'score': self.score.score})
            self.redis.json().arrappend(game_key, Path("players"), serializer.data)

            # a check
            channel_layer = get_channel_layer()
            client = Clients.get_client_by_player_id_async(self.player.id) #faut cherche le client par un autre moyen
            channel_name = self.redis.hget(name="consumers_channels", key=str(client.id))
            channel_layer.group_add(str(game.id), channel_name.decode('utf-8'))

            await send_group(self.player.id, EventType.GAME, ResponseAction.JOIN_GAME)
            await self.leave_mm()

        except Exception as e:
            await send_group_error(self.player.id, ResponseError.JOINING_ERROR)
            await self.leave_mm()
            raise RuntimeError(str(e))




# class PlayerStats(models.Model):
#     class Meta:
#         db_table = 'players_stats'

#     # ── Informations ──────────────────────────────────────────────────────────────────
#     total_game = IntegerField(default=0, blank=True)
#     wins = IntegerField(default=0, blank=True)
#     losses = IntegerField(default=0, blank=True)
#     mmr = IntegerField(default=50, blank=True)
#     # rank = ForeignKey('pong.Rank', on_delete=models.SET_NULL, null=True, blank=True, default=Ranks.BRONZE.value)
#     rank = CharField(default=Ranks.BRONZE.value, max_length=100, blank=True)
#     #I am like so sure this doesnt work because it doesnt know where pong.rank is