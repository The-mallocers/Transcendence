import os
import signal
import sys
import types

from django.apps import AppConfig


class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.game'

    def __init__(self, app_name: str, app_module: types.ModuleType | None):
        super().__init__(app_name, app_module)
        self.thread = None

    def ready(self):
        if not self.is_running_server():
            return

        from utils.threads.matchmaking import MatchmakingThread
        self.thread = MatchmakingThread("MatchmakingThread")
        self.thread.start()
        # atexit.register(self.stop_thread)
        # signal.signal(signal.SIGTERM, self.stop_thread)
        # signal.signal(signal.SIGINT, self.stop_thread)

    def stop_thread(self, signum, frame):
        if self.thread:
            self.thread.stop()
            self.thread.join()
        signal.default_int_handler(signum, frame)

    def is_running_server(self):
        base_names = [os.path.basename(arg) for arg in sys.argv]
        return any(arg in base_names for arg in
                   ('runserver', 'daphne', 'uvicorn', 'gunicorn'))
