from __future__ import annotations

import asyncio
import logging
import threading

import redis.asyncio as aioredis
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction

from apps.game.manager import GameManager
from apps.player.manager import PlayerManager
from utils.pong.enums import GameStatus

logger = logging.getLogger('apps.game')

class MatchmakingThread(threading.Thread):
    _instance = None

    def __init__(self):
        super().__init__(daemon=True)
        self.redis = None
        self.loop = None
        self.running = False

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = MatchmakingThread()
        return cls._instance

    async def main(self):
        found: bool = True
        game_manager = GameManager()
        while self.running:
            try:
                # ── Creating ──────────────────────────────────────────────────────────
                if found or await game_manager.get_status() is GameStatus.ERROR:
                    await game_manager.create_game()

                # ── Waiting ───────────────────────────────────────────────────────────
                await game_manager.set_status(GameStatus.WAITING)

                # ── Matchmaking ───────────────────────────────────────────────────────
                p1, p2 = await self.select_players()
                if p1 is None or p2 is None:
                    found = False
                    continue

                await game_manager.set_status(GameStatus.MATCHMAKING)

                await game_manager.add_player(p1)
                await self.redis.srem('matchmaking_players', p1)
                await self.send_to_websocket(f'group_{p1}', {'game_id': await game_manager.get_id(), 'player_id': str(p1)})

                await game_manager.add_player(p2)
                await self.redis.srem('matchmaking_players', p2)
                await self.send_to_websocket(f'group_{p2}', {'game_id': await game_manager.get_id(), 'player_id': str(p2)})

                found = True

            except Exception as e:
                await game_manager.set_status(GameStatus.ERROR)
                logging.error(f"Matchmaking error: {str(e)}")

            await asyncio.sleep(1)

    def stop(self):
        self.running = False
        if self.loop and self.loop.is_running():
            self.loop.run_until_complete(self.cleanup())
            self.loop.stop()
        if self.redis:
            asyncio.run(self.redis.close())

    def run(self):
        self.running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self.init_redis())
            self.loop.run_until_complete(self.cleanup())
            self.loop.run_until_complete(self.main())
        except Exception as e:
            print(f"Error in game thread: {e}")
        finally:
            self.stop()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def init_redis(self):
        self.redis = await aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0
        )
        return self.redis

    async def send_to_websocket(self, group_name, message):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            group_name,
            {
                'type': 'matchmaking_info',
                'message': message
            }
        )

    async def select_players(self):
        players_queue = await self.redis.smembers('matchmaking_players')
        players = [player.decode('utf-8') for player in players_queue]
        if len(players) >= 2: #il faudra ce base sur les mmr
            return players[0], players[1]
        return None, None

    # ── Cleaning ──────────────────────────────────────────────────────────────────────
    async def cleanup(self):
        logger.info("Cleaning up unfinished games from previous session...")
        try:
            game_keys = await self.redis.keys('game:*')

            for key in game_keys:
                game_data = await self.redis.json().get(key)
                if game_data and game_data.get('status') != GameStatus.FINISHED:
                    await self.redis.delete(key)
                    game_id = key.decode('utf-8').split(':')[1]
                    await self._delete_unfinished_game_db(int(game_id))

            active_games = await self.redis.smembers('matchmaking_players')
            for game in active_games:
                await self.redis.srem('matchmaking_players', game)

            await GameManager.cleanup()

            logger.info("Cleanup of unfinished games complete")
        except Exception as e:
            logger.error(f"Error during cleanup of unfinished games: {str(e)}")

    @staticmethod
    @sync_to_async
    def _delete_unfinished_game_db(game_id):
        from apps.game.models import Game
        with transaction.atomic():
            Game.objects.filter(
                id=game_id,
                status__in=[
                    GameStatus.CREATING,
                    GameStatus.WAITING,
                    GameStatus.MATCHMAKING,
                    GameStatus.STARTING,
                    GameStatus.RUNNING,
                    GameStatus.ENDING,
                    GameStatus.DESTROING
                ]
            ).delete()