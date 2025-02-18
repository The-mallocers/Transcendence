import logging
import signal
import sys
import types

from django.apps import AppConfig



class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.game'

    def ready(self):
        from apps.game.matchmaking import MatchmakingThread
        matchmaking_thread = MatchmakingThread()
        if not matchmaking_thread.is_alive():
            matchmaking_thread.start()

        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

    def shutdown(self, *args):
        logging.info("test")
        sys.exit(0)