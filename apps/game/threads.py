import asyncio
import logging
import threading
from abc import ABC, abstractmethod

import redis
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction
from redis import Redis

from apps.game.manager import GameManager
from apps.game.models import Game
from utils.pong.enums import GameStatus, SendType


class Threads(threading.Thread, ABC):
    instance = None

    def __init__(self):
        super().__init__(daemon=True)
        self.redis = redis.asyncio.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self._logger = logging.getLogger(self.__class__.__name__)
        self.loop = None
        self.running = False

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    def run(self):
        self.running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self.main())
        except Exception as e:
            print(f"Error in matchmaking thread: {e}")
        finally:
            self.stop()

    @abstractmethod
    def main(self):
        pass

    def stop(self):
        self.running = False
        try:
            logging.info("Cleaning up unfinished games from previous session...")

            redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
            game_keys = redis_client.keys('game:*')
            for key in game_keys:
                game_data = redis_client.json().get(key)
                if game_data and game_data.get('status') != GameStatus.FINISHED:
                    redis_client.delete(key)
                    game_id = key.decode('utf-8').split(':')[1]
                    Game.objects.filter(
                        id=game_id,
                        status__in=[
                            GameStatus.CREATING,
                            GameStatus.WAITING,
                            GameStatus.MATCHMAKING,
                            GameStatus.STARTING,
                            GameStatus.RUNNING,
                            GameStatus.ENDING,
                            GameStatus.DESTROING
                        ]
                    ).delete()

            redis_client.delete('matchmaking_queue')
            GameManager.cleanup()

            logging.info("Cleanup of unfinished games complete")
        except Exception as e:
            logging.error(f"Error during cleanup of unfinished games: {str(e)}")

        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.loop.stop)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def send_to_group(self, group_name, send_type: SendType, payload):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            group_name,
            {
                'type': 'group_send',
                'message': {
                    'send_type': send_type.value,
                    'payload': payload
                }
            }
        )

    # ── Cleaning ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def _delete_unfinished_game_db(game_id):
        logging.info(game_id)
        Game.objects.filter(
            id=game_id,
            status__in=[
                GameStatus.CREATING,
                GameStatus.WAITING,
                GameStatus.MATCHMAKING,
                GameStatus.STARTING,
                GameStatus.RUNNING,
                GameStatus.ENDING,
                GameStatus.DESTROING
            ]
        ).delete()