import asyncio
import traceback

from django.conf import settings
from redis import Redis

from apps.game.manager import GameManager
from apps.player.manager import PlayerManager
from utils.pong.enums import GameStatus, ResponseError
from utils.pong.objects import PADDLE_WIDTH, OFFSET_PADDLE, CANVAS_WIDTH
from utils.threads.game import GameThread
from utils.threads.threads import Threads
from utils.websockets.channel_send import send_group_error
from redis.commands.json.path import Path

#Game Will be the new game manager !
from apps.game.models import Game

class MatchmakingThread(Threads):
    def main(self):
        # game_manager: GameManager = None
        game = None
        
        while not self._stop_event.is_set():
            try:
                matched = self.select_players()

                if matched:
                    game = Game()  
                    self.create_game(game)
                    self._logger.info(f"Found match: {game_manager.pL} vs {game_manager.pR}")
                    game.rset_status(GameStatus.MATCHMAKING, self.redis)

                    game_manager.pL.join_game(game_manager)
                    game_manager.pL.paddle.set_x(0 + OFFSET_PADDLE)
                    game_manager.pR.join_game(game_manager)
                    game_manager.pR.paddle.set_x(CANVAS_WIDTH - OFFSET_PADDLE - PADDLE_WIDTH)
                    game_manager.rset_status(GameStatus.STARTING)
                    self.redis.hset(name="player_game", key=str(game_manager.pL.id),
                                          value=str(game_manager.get_id()))
                    self.redis.hset(name="player_game", key=str(game_manager.pR.id),
                                          value=str(game_manager.get_id()))
                    GameThread(manager=game_manager).start()
                    game_manager = None

                asyncio.sleep(1)

            except Exception as e:
                self._logger.error(str(e))
                traceback.print_exc()
                if game_manager:
                    game_manager.error_game()
                if game_manager.pL:
                    send_group_error(game_manager.pL.id, ResponseError.MATCHMAKING_ERROR)
                    game_manager.pL.leave_mm()
                if game_manager.pR:
                    send_group_error(game_manager.pR.id, ResponseError.MATCHMAKING_ERROR)
                    game_manager.pR.leave_mm()

    def cleanup(self):
        self._logger.info("Cleaning up unfinished games from previous session...")

        game_keys = self.redis.keys('game:*')
        for key in game_keys:
            self.redis.delete(key)

        self.redis.delete("consumers_channels")
        self.redis.delete("matchmaking_queue")
        self.redis.delete("player_game")

        GameManager.clean_db()
        self._logger.info("Cleanup of unfinished games complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def select_players(self, game):
        players_queue = self.redis.hgetall('matchmaking_queue')
        players = [player.decode('utf-8') for player in players_queue]
        if len(players) >= 2:  #il faudra ce base sur les mmr
            game.pl = players[0]
            game.pr = players[1]
            if game.pl is not None and game.pr is not None:
                return True
        return False
    
    def create_game(self, game):
        #We will only create the game in redis not in the DB
        from apps.game.api.serializers import GameSerializer
        
        game.id = game.pk #very important
        serializer = GameSerializer(game)
        self.redis.json().set(f'game:{game.id}', Path.root_path(), serializer.data)

        
    


