import time
import traceback

from redis.commands.json.path import Path

from apps.client.models import Clients
from utils.enums import EventType, GameStatus, RTables, ResponseAction, ResponseError
from utils.redis import RedisConnectionPool
from utils.serializers.tournament import TournamentSerializer
from utils.threads.threads import Threads
from utils.util import create_tournament_id
from utils.websockets.channel_send import send_group, send_group_error


class TournamentThread(Threads):
    def __init__(self, host):
        # Init
        self.code = create_tournament_id()
        self.redis = RedisConnectionPool.get_sync_connection()
        super().__init__(f'Tournament_{self.code}')
        
        # Tournaments settings
        self.host: Clients = host
        self.clients = []
        self.max_player = 0
        self.title = None
        self.public = False
        self.bots = False
        self.points_to_win = 0
        self.timer = 0
        
    def main(self):
        try:
            #Try to create to redis.
            self.create_tournament_redis
            while self.is_running():
                if self._starting() == False:
                    time.sleep(0.1)
                else:
                    break
            while self.is_running():
                self._running()
                self._ending()

        except Exception as e:
            self._logger.error(e)
            traceback.print_exc()
            # self.game.rset_status(GameStatus.ERROR)
            send_group_error(RTables.GROUP_GAME(self.game_id), ResponseError.EXCEPTION, close=True)
            self.stop()

    def is_running(self) -> bool:
        status = self.redis.json().get(RTables.JSON_TOURNAMENT(self.code), Path('status'))
        is_valid = not self._stop_event.is_set() and status is not GameStatus.ERROR
        return is_valid

    def cleanup(self):
        self._logger.info("Cleaning up tournament...")

        self.redis.delete(RTables.JSON_TOURNAMENT(self.code))
        self.redis.expire(f'channels:group:{RTables.GROUP_TOURNAMENT(self.code)}', 0)

        # RedisConnectionPool.close_connection(self.__class__.__name__)

        self._logger.info("Cleanup of tournament complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ EVENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def _starting(self):
        return False

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

            self._stop_event.set()
            self._stopping()

    def _stopping(self):
        # self.game.rset_status(GameStatus.FINISHED)
        # self.redis.hdel(RTables.HASH_MATCHES, self.game.pL.client_id, self.game.pR.client_id)
        # time.sleep(1)
        self.stop()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    
    def add_client(self, client):
        self.clients.append(client)
        self.redis.hset(name=RTables.HASH_TOURNAMENT_QUEUE(self.code), key=str(client.id), value=str(True))
        send_group(RTables.GROUP_TOURNAMENT(self.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_CREATED, {
            'code': self.code,
            'name': self.title
        })

    @staticmethod
    async def create_tournament_redis(code, data, redis):
        serializer = TournamentSerializer(data=data)
        if serializer.is_valid():
            await redis.json().set(RTables.JSON_TOURNAMENT(code), Path.root_path(), serializer.data)
        else:
            raise Exception(serializer.errors)
