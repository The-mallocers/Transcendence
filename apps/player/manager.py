import redis

import redis.asyncio as aioredis
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction

from apps.player.models import Player

redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class PlayerManager:
    _instance = None
    _redis = aioredis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    def __init__(self):
        self._player: Player = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = PlayerManager()
        return cls._instance

    @sync_to_async
    def exist(self, player_id):
        """Check if the game ID is a real game"""
        from apps.game.models import Player
        with transaction.atomic():
            return Player.objects.filter(id=player_id).exists()

    @sync_to_async
    def get_player_id_client(self, client_id):
        """Check if the game ID is a real game"""
        from apps.game.models import Clients
        with transaction.atomic():
            return Clients.objects.get(id=client_id).player.id