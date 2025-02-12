import json
import logging
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from django.db import transaction
from redis.asyncio import Redis
from channels.generic.websocket import AsyncWebsocketConsumer

import utils.utils
from apps.player.models import Player
from apps.shared.models import Clients

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

        channel = f'group_{str(self.player.id)}'
        logging.warn(channel)

        # Join game group
        await self.channel_layer.group_add(
            channel,
            self.channel_name
        )

        await redis_client.sadd("matchmaking_players", str(self.player.id))
        await self.accept()

    async def disconnect(self, close_code):
        if self.player:
            player_id = self.player.id.bytes.hex() if hasattr(self.player.id,'bytes') else str(self.player.id)
            await redis_client.srem("matchmaking_players", player_id)

    async def receive(self, text_data=None, bytes_data=None):
        # creer la game avec le GameManager
        # ajouter le user dans la game
        # chercher dans la liste matchmaking de redis un user qui est en recherche
        # renvoyer le code de la game
        # fermer la connexion

        # il faut regarder comment stocker la liste des game en cours
        try:
            data = json.loads(text_data)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def matchmaking_info(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ASYNC ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    @sync_to_async
    def get_player_db(self, client_id):
        with transaction.atomic():
            return Clients.objects.get(id=client_id).player
        return None
