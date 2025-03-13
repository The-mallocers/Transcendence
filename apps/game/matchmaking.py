import asyncio
import traceback

from django.conf import settings
from redis import Redis

from apps.game.game import GameThread
from apps.game.manager import GameManager
from utils.threads import Threads
from apps.player.manager import PlayerManager
from utils.pong.enums import GameStatus, ResponseError
from utils.websockets.channel_send import send_group_error


class MatchmakingThread(Threads):
    async def main(self):
        while not self._stop_event.is_set():
            game_manager: GameManager = GameManager()
            try:
                matched = await self.select_players(game_manager)

                if matched:
                    self._logger.info(f"Found match: {game_manager.p1} vs {game_manager.p2}")
                    await game_manager.create_game()
                    game_id = await game_manager.get_id()
                    await game_manager.rset_status(GameStatus.MATCHMAKING)

                    await game_manager.p1.join_game(game_manager)
                    await game_manager.p2.join_game(game_manager)
                    await game_manager.rset_status(GameStatus.STARTING)
                    await self.redis.hset(name="player_game", key=str(game_manager.p1.id), value=str(game_id))
                    await self.redis.hset(name="player_game", key=str(game_manager.p2.id), value=str(game_id))
                    GameThread(manager=game_manager, game_id=game_id).start()

                await asyncio.sleep(1)

            except Exception as e:
                self._logger.error(str(e))
                traceback.print_exc()
                if game_manager:
                    await game_manager.error_game()
                if game_manager.p1:
                    await send_group_error(game_manager.p1.id, ResponseError.MATCHMAKING_ERROR)
                    await game_manager.p1.leave_mm()
                if game_manager.p2:
                    await send_group_error(game_manager.p2.id, ResponseError.MATCHMAKING_ERROR)
                    await game_manager.p2.leave_mm()

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
            game_manager.p1 = await PlayerManager().init_player(player_id=players[0])
            game_manager.p2 = await PlayerManager().init_player(player_id=players[1])
            if game_manager.p1 is not None and game_manager.p2 is not None:
                return True
        return False
