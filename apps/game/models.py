import json
import uuid
from urllib.parse import parse_qs

import redis

from datetime import timedelta

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import models
from django.db.models import IntegerField, ForeignKey
from django.db.models.fields import BooleanField, DurationField

from apps.player.models import Player
from apps.pong.utils import RequestType
from apps.shared.models import Clients
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

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ DATABASE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    @database_sync_to_async
    def check_room_exists(self, room_name):
        try:
            GameRoom.objects.get(id=room_name)
            return True
        except GameRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def check_client_exists(self, client_id):
        try:
            Clients.objects.get(id=client_id)
            return True
        except GameRoom.DoesNotExist:
            return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ WEBSOCKET ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.pong.pong import PongLogic
        self.game_logic = PongLogic()
        self.room_group_id = None
        self.room_id = None

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_name']

        # Get client ID from query parameters
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        self.client_id = query_params.get('id', ['default'])[0]

        print(self.client_id)

        if not await self.check_client_exists(self.client_id):
            await self.close(code=403, reason='Client does not exist')
            return

        if not await self.check_room_exists(self.room_id):
            await self.close(code=403, reason='Room does not exist')
            return

        # Join room group
        self.room_group_id = f'group_{self.room_id}'
        await self.channel_layer.group_add(self.room_group_id, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_id:
            await self.channel_layer.group_discard(
                self.room_group_id,
                self.channel_name
            )
        # if self.client_id:
        #     await self.game_logic.handle_disconnect(self.room_id,
        #                                             self.client_id)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)

            response = await self.game_logic.process_action(
                client_id=self.client_id,
                data=data,
                room=self.room_id
            )

            if 'error' in response:
                await self.send(text_data=json.dumps(response))
                await self.close(code=4000)
                return

            await self.channel_layer.group_send(
                self.room_group_id,
                {
                    'type': 'game_message',
                    'message': response,
                    'sender': self.client_id
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
        if event['sender'] != self.client_id:
            await self.send(text_data=json.dumps(message))

