import time
import traceback
from time import sleep

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

from apps.game.models import Game
from utils.enums import GameStatus, EventType, ResponseAction, \
    ResponseError, PlayerSide, RTables
from utils.pong.logic import PongLogic
from utils.serializers.player import PlayerInformationSerializer
from utils.threads.threads import Threads
from utils.websockets.channel_send import send_group, send_group_error


class GameThread(Threads):
    def __init__(self, game: Game):
        super().__init__(f"GameThread[{game.code}]")
        self.game = game
        self.game_id = game.code
        self.logic: PongLogic = PongLogic(self.game, self.redis)

    def main(self):
        try:
            while self.game.tournament is not None:
                if not self._waitting_players():
                    time.sleep(2)
                else:
                    break
            while self.game_is_running():
                if not self._starting():
                    time.sleep(0.1)
                else:
                    break
            while self.game_is_running():
                self._waitting_to_start()
                self._running()
                self._ending()  # I will get this one out of this loop I swear it

        except Exception as e:
            self._logger.error(traceback.format_exc())
            self.game.rset_status(GameStatus.ERROR)
            send_group_error(RTables.GROUP_GAME(self.game_id), ResponseError.EXCEPTION, close=True)
            self.stop()

    def game_is_running(self) -> bool:
        is_valid = not self._stop_event.is_set() and self.game.rget_status() is not GameStatus.ERROR
        return is_valid

    def cleanup(self):
        self._logger.info("Cleaning up game...")

        self.redis.delete(RTables.JSON_GAME(self.game_id))
        self.redis.hdel(RTables.HASH_MATCHES, str(self.game.pL.client.id))
        self.redis.hdel(RTables.HASH_MATCHES, str(self.game.pR.client.id))
        self.redis.expire(f'channels:group:{RTables.GROUP_GAME(self.game_id)}', 0)

        # RedisConnectionPool.close_connection(self.__class__.__name__)
        self._logger.info("Cleanup of game complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ EVENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def _waitting_players(self):
        if self.game.rget_status() is GameStatus.MATCHMAKING and self.game.tournament is not None:
            channel_layer = get_channel_layer()
            both_joined = 0

            if self.redis.hexists(RTables.HASH_CLIENT(self.game.pR.client.id), EventType.GAME.value):
                channel_name_pR = self.redis.hget(name=RTables.HASH_CLIENT(self.game.pR.client.id), key=str(EventType.GAME.value))
                channel_name_pR = channel_name_pR.decode('utf-8') if channel_name_pR else None
                if channel_name_pR and self.redis.zscore(f'channels:group:{RTables.GROUP_GAME(self.game_id)}', str(channel_name_pR)) is None:
                    async_to_sync(channel_layer.group_add)(RTables.GROUP_GAME(self.game_id), channel_name_pR)
                    send_group(RTables.GROUP_CLIENT(self.game.pR.client.id), EventType.GAME, ResponseAction.JOIN_GAME)
                both_joined += 1
            if self.redis.hexists(RTables.HASH_CLIENT(self.game.pL.client.id), EventType.GAME.value):
                channel_name_pL = self.redis.hget(name=RTables.HASH_CLIENT(self.game.pL.client.id), key=str(EventType.GAME.value))
                channel_name_pL = channel_name_pL.decode('utf-8') if channel_name_pL else None
                if channel_name_pL and self.redis.zscore(f'channels:group:{RTables.GROUP_GAME(self.game_id)}', str(channel_name_pL)) is None:
                    async_to_sync(channel_layer.group_add)(RTables.GROUP_GAME(self.game_id), channel_name_pL)
                    send_group(RTables.GROUP_CLIENT(self.game.pL.client.id), EventType.GAME, ResponseAction.JOIN_GAME)
                both_joined += 1

            if both_joined == 2:
                self.game.rset_status(GameStatus.STARTING)
                return True
            else:
                return False

    def _starting(self):
        if self.game.rget_status() is GameStatus.STARTING:
            pL_serializer = PlayerInformationSerializer(self.game.pL, context={'side': PlayerSide.LEFT})
            pR_serializer = PlayerInformationSerializer(self.game.pR, context={'side': PlayerSide.RIGHT})
            send_group(RTables.GROUP_GAME(self.game_id), EventType.GAME, ResponseAction.PLAYER_INFOS, {
                'left': pL_serializer.data,
                'right': pR_serializer.data
            })
            send_group(RTables.GROUP_GAME(self.game_id), EventType.GAME, ResponseAction.STARTING)
            self.game.rset_status(GameStatus.WAITING_TO_START)
            return True
        return False

    def _waitting_to_start(self):
        if self.game.rget_status() is GameStatus.WAITING_TO_START:
            counts = 5
            while counts >= 0:
                if (counts == 0):
                    send_group(RTables.GROUP_GAME(self.game_id), EventType.GAME, ResponseAction.WAITING_TO_START, {'timer': 'GO !!!!'})
                else:
                    send_group(RTables.GROUP_GAME(self.game_id), EventType.GAME, ResponseAction.WAITING_TO_START, {'timer': counts})
                counts -= 1
                sleep(1)
            self.game.rset_status(GameStatus.RUNNING)
            return True

    def _running(self):
        if self.game.rget_status() is GameStatus.RUNNING:
            self.execute_once(send_group, self.game_id, EventType.GAME, ResponseAction.STARTED)
            self.logic.game_task()

    def _ending(self):
        if self.game.rget_status() is GameStatus.ENDING:
            if self.logic.score_pL.get_score() == self.game.points_to_win or self.logic.score_pR.get_score() == self.game.points_to_win:
                self.logic.set_result()
                send_group(RTables.GROUP_GAME(self.game_id), EventType.GAME, ResponseAction.GAME_ENDING, self.game_id, close=True)
            else:  # ya eu une erreur, genre client deco ou erreur sur le server
                self.logic.set_result(disconnect=True)
                send_group_error(RTables.GROUP_GAME(self.game_id), ResponseError.OPPONENT_LEFT, close=True)

            #VERY IMPORTANT FUNCTION ENDGAME
            if self.game.tournament is not None:
                from utils.threads.tournament import TournamentThread
                TournamentThread.set_game_players(self.game.tournament.code, self.game.code, self.game.winner, self.game.loser, self.redis)
                #Changed the above to be just the object

            self._stop_event.set()
            self._stopping()

    def _stopping(self):
        self.game.rset_status(GameStatus.FINISHED)
        self.redis.hdel(RTables.HASH_MATCHES, str(self.game.pL.client.id), str(self.game.pR.client.id))
        time.sleep(1)
        self.stop()
