import atexit
import types

from django.apps import AppConfig


class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.game'

    def __init__(self, app_name: str, app_module: types.ModuleType | None):
        super().__init__(app_name, app_module)
        self.thread = None

    def ready(self):
        from apps.game.matchmaking import MatchmakingThread
        self.thread = MatchmakingThread("MatchmakingThread")
        self.thread.start()

        atexit.register(self.stop_thread)


    def stop_thread(self):
        if self.thread:
            self.thread.stop()
            self.thread.join()