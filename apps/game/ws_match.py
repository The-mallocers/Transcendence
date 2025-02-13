import json
import logging
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction
from redis.asyncio import Redis

from apps.game.manager import GameManager
from apps.player.manager import PlayerManager
from apps.player.models import Player
from apps.shared.models import Clients
from utils.pong.enums import GameStatus

redis_client = Redis(host="localhost", port=6379, db=0)

class MatchMaking(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = None

    async def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)

        self.player: Player = await self.get_player_db(query_params.get('id', ['default'])[0])
        if self.player is None:
            await self.close(code=403)
            return

        await self.channel_layer.group_add(f'group_{str(self.player.id)}', self.channel_name)
        await redis_client.sadd("matchmaking_players", str(self.player.id))
        await self.accept()

    async def disconnect(self, close_code):
        if self.player:
            await redis_client.srem("matchmaking_players", str(self.player.id))

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)

            # ── Starting ──────────────────────────────────────────────────────────────
            if data.get('type') == 'joined':
                game_id = data.get('game_id')
                player_id = data.get('player_id')

                if not await GameManager.exist(game_id):
                    return await self.send(text_data=json.dumps({
                        'error': 'Invalid game ID'
                    }))
                if not await PlayerManager.exist(player_id):
                    return await self.send(text_data=json.dumps({
                        'error': 'Invalid player ID'
                    }))

                game_manager = await GameManager.get_instance(game_id)
                await game_manager.set_status(GameStatus.STARTING)

                await self.channel_layer.group_discard(f'group_{player_id}', self.channel_name)
                await self.close()
                return


        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))

    async def matchmaking_info(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ASYNC ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    @sync_to_async
    def get_player_db(self, client_id):
        with transaction.atomic():
            return Clients.objects.get(id=client_id).player
