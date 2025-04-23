import random
import re
import time
import traceback

from apps.game.models import Game
from apps.player.models import Player
from utils.enums import GameStatus, ResponseError, RTables, EventType
from utils.threads.game import GameThread
from utils.threads.threads import Threads
from utils.websockets.channel_send import send_group_error


class MatchmakingThread(Threads):
    def main(self):
        game: Game = Game()

        while not self._stop_event.is_set():
            try:
                if game is None:
                    game = Game()

                if self.select_players(game):
                    game.create_redis_game()
                    self._logger.info(f"Found match: {game.pL} vs {game.pR}")
                    game.rset_status(GameStatus.MATCHMAKING)

                    game.init_players()
                    game.rset_status(GameStatus.STARTING)
                    GameThread(game=game).start()
                    game = None

                time.sleep(1)

            except Exception as e:
                traceback.print_exc()
                if game:
                    game.error_game()
                if game.pL:
                    send_group_error(RTables.GROUP_CLIENT(game.pL.id), ResponseError.MATCHMAKING_ERROR)
                    game.pL.leave_queue(game.code, game.is_duel)
                if game.pR:
                    send_group_error(RTables.GROUP_CLIENT(game.pR.id), ResponseError.MATCHMAKING_ERROR)
                    game.pR.leave_queue(game.code, game.is_duel)

    def cleanup(self):
        self._logger.info("Cleaning up unfinished games from previous session...")

        # Stop all active threads (GameThread and TournamentThread instances)
        Threads.stop_all_threads(except_thread=self)

        game_keys = self.redis.keys('game:*')
        for key in game_keys:
            self.redis.delete(key)

        # self.redis.delete(RTables.HASH_CLIENT)
        self.redis.delete(RTables.HASH_G_QUEUE)
        self.redis.delete(RTables.HASH_DUEL_QUEUE('*'))
        self.redis.delete(RTables.HASH_TOURNAMENT_QUEUE('*'))
        self.redis.delete(RTables.HASH_MATCHES)

        # RedisConnectionPool.close_connection(self.__class__.__name__)

        self._logger.info("Cleanup of unfinished games complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def select_players(self, game):
        # First we check the global queue
        players_queue = self.redis.hgetall(RTables.HASH_G_QUEUE)
        players = [player.decode('utf-8') for player in players_queue]
        if len(players) >= 2:  # il faudra ce base sur les mmr
            selected_players = players[:2]  # this gets the first 2 players of the list
            random.shuffle(selected_players)
            game.is_duel = False
            game.pL = Player(selected_players[0])
            game.pR = Player(selected_players[1])
            if game.pL is not None and game.pR is not None:
                return True
        # second we check the duel for start game
        cursor = 0
        cursor, duels = self.redis.scan(cursor=cursor, match=RTables.HASH_DUEL_QUEUE('*'))
        for duel in duels:
            players = list(self.redis.hgetall(duel).items())
            random.shuffle(players)
            player_1, stat_p1 = players[0]
            player_2, stat_p2 = players[1]
            channel_p1 = self.redis.hget(name=RTables.HASH_CLIENT(player_1.decode('utf-8')), key=str(EventType.GAME.value))
            channel_p2 = self.redis.hget(name=RTables.HASH_CLIENT(player_2.decode('utf-8')), key=str(EventType.GAME.value))
            if not channel_p1 or not channel_p2:
                return False
            if stat_p1.decode('utf-8') == 'True' and stat_p2.decode('utf-8') == 'True':
                game.is_duel = True
                game.code = re.search(rf'{RTables.HASH_DUEL_QUEUE("")}(\w+)$', duel.decode('utf-8')).group(1)
                game.game_key = RTables.JSON_GAME(game.code)
                game.pL = Player(player_1.decode('utf-8'))
                game.pR = Player(player_2.decode('utf-8'))
                return True
        return False
