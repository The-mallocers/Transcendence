import asyncio
import enum
import inspect
import logging
import threading
from abc import ABC, abstractmethod

from django.conf import settings
from redis.asyncio import Redis


class Threads(threading.Thread, ABC):
    instance = None

    def __init__(self, name):
        super().__init__(daemon=True, name=name)
        self.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._stop_event = threading.Event()
        self.loop = asyncio.new_event_loop()
        self._completed_actions = set()

    def run(self):
        self._logger.info(f"Starting thread [{self.name}]")
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.main())

    def stop(self):
        self._logger.info(f"Stopping thread [{self.name}]")
        self._stop_event.set()
        self.cleanup()

    async def execute_once(self, action_func, *args, **kwargs):
        frame = inspect.currentframe().f_back
        caller_name = frame.f_code.co_name
        func_name = action_func.__name__
        args_str = ""
        for arg in args:
            if isinstance(arg, (str, int, float, bool, enum.Enum)):
                args_str += f"_{str(arg)}"
        action_id = f"{self.name}_{caller_name}_{func_name}{args_str}"

        if action_id not in self._completed_actions:
            await action_func(*args, **kwargs)
            self._completed_actions.add(action_id)
            self._logger.debug(f"Action '{action_id}' executed")
            return True
        return False

    @abstractmethod
    async def main(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass