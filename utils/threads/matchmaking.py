import asyncio
import traceback

from redis.commands.json.path import Path

from apps.game.manager import GameManager
from apps.game.models import Game
from apps.player.models import Player
from utils.pong.enums import GameStatus, ResponseError
from utils.threads.game import GameThread
from utils.threads.threads import Threads
from utils.websockets.channel_send import send_group_error


# Game Will be the new game manager !
class MatchmakingThread(Threads):
    def main(self):
        game: Game = None
        matched: bool = False
        
        while not self._stop_event.is_set():
            try:
                if game:
                    matched = self.select_players(game)
                else:
                    game = Game()

                if matched:
                    self.create_game(game)
                    self._logger.info(f"Found match: {game.pL} vs {game.pR}")
                    game.rset_status(GameStatus.MATCHMAKING)

                    game.pL.join_game(game)
                    game.pR.join_game(game)
                    # game.pL.paddle.set_x(0 + OFFSET_PADDLE)
                    # game.pR.paddle.set_x(CANVAS_WIDTH - OFFSET_PADDLE - PADDLE_WIDTH)
                    game.rset_status(GameStatus.STARTING)
                    self.redis.hset(name="player_game", key=str(game.pL.id),
                                    value=str(game.get_id()))
                    self.redis.hset(name="player_game", key=str(game.pR.id),
                                    value=str(game.get_id()))
                    GameThread(manager=game).start()
                    game = None

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
            game.pL = Player.get_player_by_client(players[0])
            game.pR = Player.get_player_by_client(players[1])
            if game.pL is not None and game.pR is not None:
                return True
        return False
    
    def create_game(self, game):
        #We will only create the game in redis not in the DB
        from apps.game.api.serializers import GameSerializer
        
        serializer = GameSerializer(game)
        self.redis.json().set(game.game_key, Path.root_path(), serializer.data)
