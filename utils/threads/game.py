import time
import time
import traceback

from apps.game.models import Game
from apps.player.api.serializers import PlayerInformationSerializer
from apps.pong.pong import PongLogic
from utils.pong.enums import GameStatus, EventType, ResponseAction, \
    ResponseError, Side
from utils.threads.threads import Threads
from utils.websockets.channel_send import send_group, send_group_error


class GameThread(Threads):
    def __init__(self, game: Game):
        super().__init__(f"Game_{game.game_id}")
        self.game = game
        self.game_id = game.game_id
        self.logic: PongLogic = PongLogic(self.game, self.redis)

    def main(self):
        try:
            while self.game_is_running():
                if self._starting() == False:
                    time.sleep(0.1)
                else:
                    break
            while self.game_is_running():
                self._running()
                self._ending()  # I will get this one out of this loop I swear it

        except Exception as e:
            self._logger.error(e)
            traceback.print_exc()
            self.game.rset_status(GameStatus.ERROR)
            send_group_error(self.game_id, ResponseError.EXCEPTION, close=True)
            self.stop()

    def game_is_running(self) -> bool:
        is_valid = not self._stop_event.is_set() and self.game.rget_status() is not GameStatus.ERROR
        return is_valid

    def cleanup(self):
        self._logger.info("Cleaning up game...")

        self.redis.delete(f'game:{self.game_id}')
        self.redis.hdel('current_matches', str(self.game.pL.client_id))
        self.redis.hdel('current_matches', str(self.game.pR.client_id))
        self.redis.delete(f'channels::group:{self.game_id}')
        # RedisConnectionPool.close_connection(self.__class__.__name__)

        self._logger.info("Cleanup of game complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ EVENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def _starting(self):
        if self.game.rget_status() is GameStatus.STARTING:
            send_group(self.game_id, EventType.GAME, ResponseAction.STARTING)
            pL_serializer = PlayerInformationSerializer(self.game.pL, context={'side': Side.LEFT})
            pR_serializer = PlayerInformationSerializer(self.game.pR, context={'side': Side.RIGHT})
            send_group(self.game_id, EventType.GAME, ResponseAction.PLAYER_INFOS, {
                'left': pL_serializer.data,
                'right': pR_serializer.data
            })
            self.game.rset_status(GameStatus.RUNNING)
            time.sleep(5)
            return True
        return False

    def _running(self):
        if self.game.rget_status() is GameStatus.RUNNING:
            self.execute_once(send_group, self.game_id, EventType.GAME, ResponseAction.STARTED)
            self.logic.game_task()

    def _ending(self):
        if self.game.rget_status() is GameStatus.ENDING:
            if self.logic.score_pL.get_score() == self.game.points_to_win or self.logic.score_pR.get_score() == self.game.points_to_win:
                self.logic.set_result()
                send_group(self.game_id, EventType.GAME, ResponseAction.GAME_ENDING, self.game_id)
            else:  # ya eu une erreur, genre client deco ou erreur sur le server
                self.logic.set_result(error=True)
                send_group_error(self.game_id, ResponseError.OPPONENT_LEFT, close=True)

            self._stop_event.set()
            self._stopping()

    def _stopping(self):
        self.game.rset_status(GameStatus.FINISHED)
        self.redis.hdel('player_game', self.game.pL.client_id, self.game.pR.client_id)
        time.sleep(1)
        self.stop()
