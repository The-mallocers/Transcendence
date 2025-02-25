import asyncio
import logging
import threading
from abc import ABC, abstractmethod

from channels.layers import get_channel_layer
from django.conf import settings
from redis.asyncio import Redis
from redis.commands.json import JSON

from utils.pong.enums import EventType


class Threads(threading.Thread, ABC):
    instance = None

    def __init__(self, name):
        super().__init__(daemon=True, name=name)
        self.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self.json_redis = JSON(self.redis)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._stop_event = threading.Event()
        self.loop = asyncio.new_event_loop()

    def run(self):
        self._logger.info(f"Starting thread [{self.name}]")
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.main())

    def stop(self):
        self._logger.info(f"Stopping thread [{self.name}]")
        self._stop_event.set()
        self.cleanup()

    @abstractmethod
    async def main(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass