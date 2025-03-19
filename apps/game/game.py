import asyncio
import traceback

from asgiref.sync import sync_to_async
from django.conf import settings
from redis import Redis

from apps.game.manager import GameManager
from apps.player.api.serializers import PlayerInformationSerializer
from apps.pong.pong import PongLogic
from utils.pong.enums import GameStatus, EventType, ResponseAction, ResponseError
from utils.pong.objects.ball import Ball
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score
from utils.threads import Threads
from utils.websockets.channel_send import send_group, send_group_error


class GameThread(Threads):
    def __init__(self, manager: GameManager):
        super().__init__(f"Game_{manager.get_id()}")
        self.game_manager = manager
        self.game_manager._redis = self.redis
        self.game_id = manager.get_id()
        self.logic: PongLogic = None

    async def main(self):
        try:
            initialized = await self.init_game()
            while not self._stop_event.is_set() and initialized and await self.game_manager.rget_status() is not GameStatus.ERROR:
                if await self._starting():
                    break
            while not self._stop_event.is_set() and initialized and await self.game_manager.rget_status() is not GameStatus.ERROR:
                await self._running()
                await self._ending()

        except Exception as e:
            self._logger.error(e)
            traceback.print_exc()
            await self.game_manager.rset_status(GameStatus.ERROR)
            await send_group_error(self.game_id, ResponseError.EXCEPTION, close=True)
            self.stop()

    def cleanup(self):
        self._logger.info("Cleaning up game...")

        redis_sync = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        redis_sync.delete(f'game:{self.game_id}')
        redis_sync.hdel('player_game', str(self.game_manager.pL.id))
        redis_sync.hdel('player_game', str(self.game_manager.pR.id))
        redis_sync.close()

        self._logger.info("Cleanup of game complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GAME FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def init_game(self):
        self.game_manager._redis = self.redis
        
        self.logic: PongLogic = PongLogic(
            self.game_manager,
            Ball(self.redis, self.game_id),
            Paddle(self.redis, self.game_id, self.game_manager.pL.id),
            Paddle(self.redis, self.game_id, self.game_manager.pR.id),
            Score(self.redis, self.game_id, self.game_manager.pL.id),
            Score(self.redis, self.game_id, self.game_manager.pR.id),
        )
        
        return True

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ EVENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def _starting(self):
        if await self.game_manager.rget_status() is GameStatus.STARTING:
            await send_group(self.game_id, EventType.GAME, ResponseAction.STARTING)
            pL_serializer = PlayerInformationSerializer(self.game_manager.pL.player,
                                                        context={'id': self.game_manager.pL.id, 'paddle': self.game_manager.pL.paddle})
            pR_serializer = PlayerInformationSerializer(self.game_manager.pR.player,
                                                        context={'id': self.game_manager.pR.id, 'paddle': self.game_manager.pR.paddle})
            pL_data = await sync_to_async(lambda: pL_serializer.data)()
            pR_data = await sync_to_async(lambda: pR_serializer.data)()
            await send_group(self.game_id, EventType.GAME, ResponseAction.PLAYER_INFOS, {
                'left': pL_data,
                'right': pR_data
            })
            await asyncio.sleep(5)
            return True
        return False

    async def _running(self):
        if await self.game_manager.rget_status() is GameStatus.RUNNING:
            await self.execute_once(send_group, self.game_id, EventType.GAME, ResponseAction.STARTED)
            await self.logic.game_task()

    async def _ending(self):
        if await self.game_manager.rget_status() is GameStatus.ENDING:
            await self.game_manager.set_result()
            
            self._stop_event.set()
            await self._stoping()

    async def _stoping(self):
        await self.game_manager.rset_status(GameStatus.FINISHED)
        await self.redis.hdel('player_game', self.game_manager.pL.id, self.game_manager.pR.id)
        await asyncio.sleep(1)
        #Sending the return message before stopping, maybe bad maybe good idk
        await send_group(self.game_id, EventType.ENDGAME, ResponseAction.ENDGAME, {
                # 'left': pL_data,
                # 'right': pR_data
            })
        self.stop()
