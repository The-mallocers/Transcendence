import asyncio
import logging

from apps.game.manager import GameManager
from apps.game.threads import Threads
from utils.pong.enums import GameStatus


class GameThread(Threads):
    def __init__(self, game_id):
        super().__init__()
        self.game_id = game_id

    async def main(self):
        found: bool = True
        game_manager = GameManager()
        while self.running:
            try:
                logging.info(self.game_id)
            except Exception as e:
                await game_manager.set_status(GameStatus.ERROR)
                logging.error(e)

            await asyncio.sleep(5)