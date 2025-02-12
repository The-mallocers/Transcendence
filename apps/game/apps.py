from django.apps import AppConfig



class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.game'

    def ready(self):
        from apps.game.matchmaking import MatchmakingThread
        game_thread = MatchmakingThread.get_instance()
        if not game_thread.is_alive():
            game_thread.start()
