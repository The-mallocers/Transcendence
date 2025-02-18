import logging
import signal
import sys

from django.apps import AppConfig


class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.game'

    def ready(self):
        from apps.game.matchmaking import MatchmakingThread

        self.matchmaking_thread = MatchmakingThread()
        if not self.matchmaking_thread.is_alive():
            self.matchmaking_thread.start()

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        logging.info("Stopping background thread...")
        if hasattr(self, 'matchmaking_thread'):
            self.matchmaking_thread.stop()
            self.matchmaking_thread.join()