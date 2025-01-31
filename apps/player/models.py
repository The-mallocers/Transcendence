import uuid

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import models
from django.db.models import ManyToManyField, ImageField, ForeignKey
from django.db.models.fields import CharField, IntegerField

from apps.pong.utils import Paddle, CANVAS_HEIGHT


class Rank(models.Model):
    class Meta:
        db_table = 'ranks_list'

    name = CharField(primary_key=True, max_length=100, editable=False, null=False)
    icon = ImageField(upload_to='rank_icon/', null=False)
    mmr_min = IntegerField(null=False)
    mmr_max = IntegerField(null=False)

class Player(models.Model, AsyncWebsocketConsumer):
    class Meta:
        db_table = 'client_player'

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)

    # ── Game Info ─────────────────────────────────────────────────────────────────────
    score = IntegerField(default=0)
    position = CharField(max_length=5, null=True)
    paddle = Paddle()

    # ━━ PLAYER INFOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    nickname = CharField(max_length=20, null=True, editable=False)
    friends = ManyToManyField('self', symmetrical=False, blank=True, related_name='friends_with')
    firends_requests = ManyToManyField('self', symmetrical=False, blank=True, related_name='invited_by')
    firends_invitations = ManyToManyField('self', symmetrical=False, blank=True, related_name='requested_by')
    mmr = IntegerField(default=100, blank=True)
    rank = ForeignKey('Rank', on_delete=models.SET_NULL, null=True, blank=True)

    # ── Custom ──────────────────────────────────────────────────────────────────────── #
    skin_ball = CharField(max_length=100, null=True) #A voir quel field il faut mettre
    skin_paddle = CharField(max_length=100, null=True)

    # ── Stats ───────────────────────────────────────────────────────────────────────── #
    game_win = IntegerField(default=0)
    game_loose = IntegerField(default=0)
    tournament_win = IntegerField(default=0)
    tournament_loose = IntegerField(default=0)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __str__(self):
        return f"Player '{str(self.nickname)}' with {self.mmr} mmr."

    async def async_save(self, *args, **kwargs):
        await sync_to_async(self.save)(*args, **kwargs)

    async def move(self, direction: str):
        if direction == 'up':
            self.paddle.y += 1 # max(0, self.paddle.y - self.paddle.speed)
        if direction == 'down':
            limit = CANVAS_HEIGHT - self.paddle.height
            self.paddle.y -= 1 # min(limit, self.paddle.y + self.paddle.speed)
        await  self.async_save()
