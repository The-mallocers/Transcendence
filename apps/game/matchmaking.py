import asyncio
import logging
import pickle

from django.conf import settings
from redis import Redis

from apps.game.game import GameThread
from apps.game.manager import GameManager
from apps.game.models import Game
from apps.game.threads import Threads
from apps.player.manager import PlayerManager
from apps.player.models import Player
from utils.pong.enums import GameStatus, EventType, ResponseError
from utils.sender import send_player_error


class MatchmakingThread(Threads):
    def __init__(self, name):
        super().__init__(name)
        self.p1: PlayerManager = None
        self.p2: PlayerManager = None

    async def main(self):
        while not self._stop_event.is_set():
            game_manager = None
            try:
                matched = await self.select_players()

                if matched:
                    self._logger.info(f"Found match: {self.p1} vs {self.p2}")
                    game_manager = GameManager()
                    await game_manager.create_game()
                    game_id = await game_manager.get_id()
                    await game_manager.set_status(GameStatus.MATCHMAKING)

                    await self.p1.join_game(game_manager)
                    await self.p2.join_game(game_manager)

                    await game_manager.set_status(GameStatus.STARTING)
                    p1_id = await self.p1.get_id()
                    p2_id = await self.p2.get_id()
                    await self.redis.set(f"active_game:{p1_id}", str(game_id))
                    await self.redis.set(f"active_game:{p2_id}", str(game_id))

                    GameThread(manager=game_manager, game_id=game_id, p1=self.p1, p2=self.p2).start()

                await asyncio.sleep(1)

            except Exception as e:
                self._logger.error(str(e))
                if game_manager:
                    await game_manager.error_game()
                if self.p1:
                    await send_player_error(await self.p1.get_id(), ResponseError.MATCHMAKING_ERROR)
                    await self.p1.leave_mm()
                if self.p2:
                    await send_player_error(await self.p2.get_id(), ResponseError.MATCHMAKING_ERROR)
                    await self.p2.leave_mm()


    def cleanup(self):
        self._logger.info("Cleaning up unfinished games from previous session...")

        redis_sync = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,db=0)

        game_keys = redis_sync.keys('game:*')
        for key in game_keys:
            redis_sync.delete(key)

        users_ws = redis_sync.keys('user_ws:*')
        for channels in users_ws:
            redis_sync.delete(channels)

        redis_sync.delete("matchmaking_queue")

        GameManager.clean_db()
        self._logger.info("Cleanup of unfinished games complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def select_players(self):
        players_queue = await self.redis.hgetall('matchmaking_queue')
        players = [player.decode('utf-8') for player in players_queue]
        if len(players) >= 2: #il faudra ce base sur les mmr
            self.p1 = await PlayerManager.init_player(players[0])
            self.p2 = await PlayerManager.init_player(players[1])
            if self.p1 is not None and self.p2 is not None:
                return True
        return False