import json
import uuid
import redis

from datetime import timedelta

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import models
from django.db.models import IntegerField, ForeignKey
from django.db.models.fields import BooleanField, DurationField

from apps.player.models import Player
from apps.pong.utils import RequestType
from utils.utils import generate_unique_code

redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class GameRoom(models.Model, AsyncWebsocketConsumer):
    class Meta:
        db_table = 'games'

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ PRIMARY FIEDLS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)

    # ── Game Informations ───────────────────────────────────────────────────────────── #
    is_active = BooleanField(editable=True, default=False, null=False)
    in_tounament = BooleanField(editable=False, default=False, null=False)
    timer = DurationField(default=timedelta(minutes=0), editable=False, null=True) #In default there is no timer
    code = IntegerField(editable=False, null=False, default=generate_unique_code, unique=True)
    # mode = ForeignKey('GameMode', on_delete=models.SET_NULL, null=True) Add game mode with another model

    # ── Players ────────────────────────────────────────────────────────────────── #
    p1 = ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player_right', editable=False)
    p2 = ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player_left', editable=False)
    winner = ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='winner', editable=False, blank=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __str__(self):
        return f"Game room id: {str(self.id)}\nIs active: {self.is_active}\nPlayer 1: {self.p1}\nPlayer 2: {self.p2}\n-------------------"

    async def async_save(self, *args, **kwargs):
        await sync_to_async(self.save)(*args, **kwargs)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ WEBSOCKET ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.pong.pong import PongLogic
        self.game_logic = PongLogic()
        self.room_group_name = None
        self.room_name = None
        self.player_id = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'group_{self.room_name}'

        try:
            await sync_to_async(GameRoom.objects.get)(id=self.room_name)
        except GameRoom.DoesNotExist:
            await self.close(code=403, reason='Room does not exist')
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        if self.player_id:
            await self.game_logic.handle_disconnect(self.room_name,
                                                    self.player_id)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            action: RequestType = RequestType(data.get('action'))

            response = await self.game_logic.process_action(
                action=action,
                data=data,
                room=self.room_name
            )

            if 'error' in response:
                await self.send(text_data=json.dumps(response))
                await self.close(code=4000)
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': response
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def game_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

