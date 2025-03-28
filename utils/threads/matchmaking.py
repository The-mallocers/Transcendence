import random
import time
import traceback

from apps.game.models import Game
from apps.player.models import Player
from utils.pong.enums import GameStatus, ResponseError
from utils.threads.game import GameThread
from utils.threads.threads import Threads
from utils.websockets.channel_send import send_group_error


# Game Will be the new game manager !
class MatchmakingThread(Threads):
    def main(self):
        game: Game = Game()
        matched: bool = False

        while not self._stop_event.is_set():
            try:
                if game is None:
                    game = Game()

                matched = self.select_players(game)
                if matched:
                    game.create_redis_game()
                    self._logger.info(f"Found match: {game.pL} vs {game.pR}")
                    game.rset_status(GameStatus.MATCHMAKING)

                    game.init_players()
                    GameThread(game=game).start()
                    game = None

                time.sleep(1)

            except Exception as e:
                print(str(e))
                traceback.print_exc()
                pass
                if game:
                    game.error_game()
                if game.pL:
                    send_group_error(game.pL.id, ResponseError.MATCHMAKING_ERROR)
                    game.pL.leave_queue()
                if game.pR:
                    send_group_error(game.pR.id, ResponseError.MATCHMAKING_ERROR)
                    game.pR.leave_queue()

    def cleanup(self):
        self._logger.info("Cleaning up unfinished games from previous session...")

        game_keys = self.redis.keys('game:*')
        for key in game_keys:
            self.redis.delete(key)

        self.redis.delete("consumers_channels")
        self.redis.delete("matchmaking_queue")
        self.redis.delete("current_matches")

        # RedisConnectionPool.close_connection(self.__class__.__name__)

        self._logger.info("Cleanup of unfinished games complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def select_players(self, game):
        players_queue = self.redis.hgetall('matchmaking_queue')
        players = [player.decode('utf-8') for player in players_queue]
        if len(players) >= 2:  # il faudra ce base sur les mmr
            selected_players = players[:2]  # this gets the first 2 players of the list
            random.shuffle(selected_players)
            game.pL = Player(selected_players[0])
            game.pR = Player(selected_players[1])
            if game.pL is not None and game.pR is not None:
                return True
        return False
