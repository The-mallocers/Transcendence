import asyncio
import logging

from apps.game.game import GameThread
from apps.game.manager import GameManager
from apps.game.models import Game
from apps.game.threads import Threads
from apps.player.models import Player
from utils.pong.enums import GameStatus, SendType


class MatchmakingThread(Threads):
    async def main(self):
        found: bool = True
        game_manager = GameManager()
        while self.running:
            try:
                # Check for players in queue
                p1, p2 = await self.select_players()

                if p1 is not None and p2 is not None:
                    self._logger.info(f"Found match: {p1} vs {p2}")

                    await game_manager.create_game()
                    await game_manager.set_status(GameStatus.MATCHMAKING)

                    await game_manager.add_player(p1)
                    await self.redis.hdel('matchmaking_queue', p1)
                    await self.send_to_group(f'player_{p1}',
                                             SendType.MATCHMAKING,
                                             'join game')

                    await game_manager.add_player(p2)
                    await self.redis.hdel('matchmaking_queue', p2)
                    await self.send_to_group(f'player_{p2}',
                                             SendType.MATCHMAKING,
                                             'join game')

                    await game_manager.set_status(GameStatus.STARTING)
                    game_id = await game_manager.get_id()
                    GameThread(game_id=game_id).start()

                await asyncio.sleep(1)

            # Getter excpetion
            except (Game.DoesNotExist, Player.DoesNotExist) as e:
                await game_manager.set_status(GameStatus.ERROR)
                logging.error(e)

            # Value excpetion
            except ValueError as e:
                await game_manager.set_status(GameStatus.ERROR)
                logging.error(e)

            except Exception as e:
                await game_manager.set_status(GameStatus.ERROR)
                logging.error(e)

        logging.info("Loop finished")

    async def select_players(self):
        players_queue = await self.redis.hgetall('matchmaking_queue')
        players = [player.decode('utf-8') for player in players_queue]
        if len(players) >= 2: #il faudra ce base sur les mmr
            return players[0], players[1]
        return None, None