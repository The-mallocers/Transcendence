import enum
import inspect
import logging
import threading
from abc import ABC, abstractmethod

from channels.layers import get_channel_layer

from utils.redis import RedisConnectionPool


class Threads(threading.Thread, ABC):
    instance = None
    active_threads = []
    _shutdown_lock = threading.Lock()

    def __init__(self, name):
        super().__init__(daemon=True, name=name)
        self.redis = RedisConnectionPool.get_sync_connection(name)

        self._logger = logging.getLogger(self.__class__.__module__)
        self._stop_event = threading.Event()
        self._completed_actions = set()
        self._channel_layer = get_channel_layer()

        # Add this thread to the active threads list
        Threads.active_threads.append(self)

    def run(self):
        self._logger.warning(f"Starting thread [{self.name}]")
        self.main()

    def stop(self):
        self._logger.warning(f"Stopping thread [{self.name}]")
        self._stop_event.set()
        self.cleanup()

        RedisConnectionPool.close_sync_connection(self.name)

        # Remove this thread from the active threads list
        if self in Threads.active_threads:
            Threads.active_threads.remove(self)

    def execute_once(self, action_func, *args, **kwargs):
        frame = inspect.currentframe().f_back
        caller_name = frame.f_code.co_name
        func_name = action_func.__name__
        args_str = ""
        for arg in args:
            if isinstance(arg, (str, int, float, bool, enum.Enum)):
                args_str += f"_{str(arg)}"
        action_id = f"{self.name}_{caller_name}_{func_name}{args_str}"

        if action_id not in self._completed_actions:
            action_func(*args, **kwargs)
            self._completed_actions.add(action_id)
            return True
        return False

    @abstractmethod
    def main(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @classmethod
    def stop_all_threads(cls, except_thread=None):
        logger = logging.getLogger(cls.__module__)

        active_count = sum(1 for t in Threads.active_threads if t != except_thread and t.is_alive())
        logger.info(f"Stopping all active threads ({active_count} threads)...")

        for thread in list(Threads.active_threads):
            if thread != except_thread and thread.is_alive():
                thread.stop()

        remaining = sum(1 for t in Threads.active_threads if t != except_thread and t.is_alive())
        logger.info(f"Thread cleanup complete. Remaining active threads: {remaining}")
