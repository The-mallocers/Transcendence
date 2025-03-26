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


class MatchmakingThread(Threads):
    async def main(self):
        game_manager: GameManager = None
        while not self._stop_event.is_set():
            try:
                if game_manager is None:
                    game_manager = GameManager()

                matched = await self.select_players(game_manager)

                if matched:
                    await game_manager.create_game()
                    self._logger.info(f"Found match: {game_manager.pL} vs {game_manager.pR}")
                    await game_manager.rset_status(GameStatus.MATCHMAKING)

                    await game_manager.pL.join_game(game_manager)
                    await game_manager.pL.paddle.set_x(0 + OFFSET_PADDLE)
                    await game_manager.pR.join_game(game_manager)
                    await game_manager.pR.paddle.set_x(CANVAS_WIDTH - OFFSET_PADDLE - PADDLE_WIDTH)
                    await game_manager.rset_status(GameStatus.STARTING)
                    await self.redis.hset(name="player_game", key=str(game_manager.pL.id),
                                          value=str(game_manager.get_id()))
                    await self.redis.hset(name="player_game", key=str(game_manager.pR.id),
                                          value=str(game_manager.get_id()))
                    GameThread(manager=game_manager).start()
                    game_manager = None

                await asyncio.sleep(5)

            except Exception as e:
                self._logger.error(str(e))
                traceback.print_exc()
                if game_manager:
                    await game_manager.error_game()
                if game_manager.pL:
                    await send_group_error(game_manager.pL.id, ResponseError.MATCHMAKING_ERROR)
                    await game_manager.pL.leave_mm()
                if game_manager.pR:
                    await send_group_error(game_manager.pR.id, ResponseError.MATCHMAKING_ERROR)
                    await game_manager.pR.leave_mm()

    def cleanup(self):
        self._logger.info("Cleaning up unfinished games from previous session...")

        redis_sync = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

        game_keys = redis_sync.keys('game:*')
        for key in game_keys:
            redis_sync.delete(key)

        redis_sync.delete("consumers_channels")
        redis_sync.delete("matchmaking_queue")
        redis_sync.delete("player_game")

        GameManager.clean_db()
        self._logger.info("Cleanup of unfinished games complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def select_players(self, game_manager):
        players_queue = await self.redis.hgetall('matchmaking_queue')
        players = [player.decode('utf-8') for player in players_queue]
        if len(players) >= 2:  #il faudra ce base sur les mmr
            #Game.pL = player_id=players[0]
            #Game.pR = player_id=players[0]
            game_manager.pL = PlayerManager(player_id=players[0])
            game_manager.pR = PlayerManager(player_id=players[1])
            if game_manager.pL is not None and game_manager.pR is not None:
                return True
        return False
