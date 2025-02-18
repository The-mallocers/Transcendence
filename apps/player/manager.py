import redis
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction
from redis.asyncio import Redis

from apps.player.models import Player
from apps.player.models import PlayerGame
from apps.shared.models import Clients

class PlayerManager:
    _instance = None
    _redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    def __init__(self):
        self._player: Player = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = PlayerManager()
        return cls._instance

    @sync_to_async
    def get_player_db(self, player_id):
        """Get player from data base"""
        try:
            with transaction.atomic():
                return Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return None

    @sync_to_async
    def get_player_game_db(self, player_id):
        """Get player game with player_id from data base"""
        try:
            with transaction.atomic():
                return PlayerGame.objects.filter(player__id=player_id).first()
        except PlayerGame.DoesNotExist:
            return None

    @sync_to_async
    def get_player_from_client_db(self, client_id) -> Player | None:
        """Get player with client id from data base"""
        try:
            with transaction.atomic():
                return Clients.objects.select_related('player__stats').get(id=client_id).player
        except Clients.DoesNotExist:
            return None

    @sync_to_async
    def get_player_id_db(self, player_game: PlayerGame):
        """Get player from data base"""
        with transaction.atomic():
            return player_game.player.id