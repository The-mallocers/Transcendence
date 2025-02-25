import asyncio

from channels.layers import channel_layers, get_channel_layer

from apps.game.manager import GameManager
from apps.game.threads import Threads
from apps.player.manager import PlayerManager
from utils.pong.enums import GameStatus, EventType, ResponseAction
from utils.pong.objects import FPS
from utils.sender import send_game, send_player


class GameThread(Threads):
    def __init__(self, manager: GameManager, game_id, p1, p2):
        super().__init__(f"Game_{game_id}")
        self.game_manager = manager
        self.game_id = game_id
        self.p1_manager : PlayerManager = p1
        self.p1_id = None
        self.p2_manager : PlayerManager = p2
        self.p2_id = None

    async def main(self):
        if await self.init_game() and await self.game_manager.get_status() is not GameStatus.ERROR:
            await self._game_task()
        self.stop()

    def cleanup(self):
        pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GAME FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def init_game(self):
        self.p1_id = await self.p1_manager.get_id()
        self.p2_id = await self.p2_manager.get_id()

        return True

    async def _game_task(self):
        try:
            while not self._stop_event.is_set():
                if await self.game_manager.get_status() != GameStatus.RUNNING:
                    await self.game_manager.load_by_id(self.game_id)
                    await asyncio.sleep(5)
                else:
                    self._logger.info('time')
                    await send_game(self.game_id, EventType.GAME, ResponseAction.TEST)

        except Exception as e:
            await self.game_manager.set_status(GameStatus.ERROR)
            self._logger.error(e)


