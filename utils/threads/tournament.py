import traceback
from time import sleep

from asgiref.sync import sync_to_async
from redis.commands.json.path import Path

from apps.client.models import Clients
from utils.enums import EventType, GameStatus, RTables, ResponseAction, ResponseError, TournamentStatus
from utils.serializers.tournament import TournamentSerializer
from utils.threads.threads import Threads
from utils.util import create_tournament_id
from utils.websockets.channel_send import send_group, send_group_error


class TournamentThread(Threads):
    def __init__(self, host, code):
        # Init
        self.code = code
        super().__init__(f'Tournament_{self.code}')

        # Tournaments settings
        self.host: Clients = host
        self.clients = [host]
        self.max_players = self.get('max_players')
        self.title = self.get('title')
        self.public = self.get('public')
        self.bots = self.get('bots')
        self.points_to_win = self.get('points_to_win')
        self.timer = self.get('timer')
        self.status: TournamentStatus = TournamentStatus(self.get('status'))

    def main(self):
        try:
            self.set_status(TournamentStatus.WAITING)
            while self.is_running():
                if not self._waitting():
                    sleep(5)
                if not self._starting():
                    sleep(0.1)
                self._running()
                self._ending()

        except Exception as e:
            self._logger.error(traceback.format_exc())
            self.set_status(TournamentStatus.ERROR)
            send_group_error(RTables.GROUP_GAME(RTables.GROUP_TOURNAMENT(self.code)), ResponseError.EXCEPTION, close=True)
        finally:
            self.stop()

    def cleanup(self):
        self._logger.info("Cleaning up tournament...")

        self.redis.delete(RTables.JSON_TOURNAMENT(self.code))
        self.redis.expire(f'channels:group:{RTables.GROUP_TOURNAMENT(self.code)}', 0)

        # RedisConnectionPool.close_connection(self.__class__.__name__)

        self._logger.info("Cleanup of tournament complete")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ EVENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def _waitting(self):
        if self.status is TournamentStatus.WAITING:
            send_group(RTables.GROUP_TOURNAMENT(self.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_WAITTING_PLAYERS)
            queue = self.redis.hgetall(RTables.HASH_TOURNAMENT_QUEUE(self.code))
            players = len(queue.items())
            if players > len(self.clients):
                last_client_id = list(queue.keys())[-1]
                last_client = Clients.get_client_by_id(last_client_id.decode('utf-8'))
                self.clients.append(last_client)
                send_group(RTables.GROUP_TOURNAMENT(self.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_PLAYER_JOIN,
                           {'id': str(last_client.id)})
            if players == self.max_players:
                self.set_status(TournamentStatus.CREATING_MATCH)
                send_group(RTables.GROUP_TOURNAMENT(self.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_PLAYERS_READY)
                return True
        return False

    def _starting(self):
        if self.status is TournamentStatus.CREATING_MATCH:
            print('creating match.')
        return False

    def _running(self):
        if self.status is TournamentStatus.WAITING:
            pass

    def _ending(self):
        if self.status is TournamentStatus.RUNNING:
            pass

    def _stopping(self):
        self.stop()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def is_running(self) -> bool:
        self.status = TournamentStatus(self.redis.json().get(RTables.JSON_TOURNAMENT(self.code), Path('status')))
        host = self.redis.hexists(RTables.HASH_TOURNAMENT_QUEUE(self.code), str(self.host.id))
        is_valid = not self._stop_event.is_set() and self.status is not GameStatus.ERROR
        if not host or not is_valid:
            if not host:
                send_group_error(RTables.GROUP_TOURNAMENT(self.code), ResponseError.HOST_LEAVE)
            self.stop()
            return False
        return True

    @staticmethod
    async def create_tournament(data, redis):
        code = await sync_to_async(create_tournament_id)()
        serializer = TournamentSerializer(data=data)
        if serializer.is_valid():
            await redis.json().set(RTables.JSON_TOURNAMENT(code), Path.root_path(), serializer.data)
            return code
        else:
            raise KeyError(serializer.error_messages)

    def set_status(self, status: TournamentStatus):
        self.status = status
        self.redis.json().set(RTables.JSON_TOURNAMENT(self.code), Path('status'), status)

    def get(self, key):
        return self.redis.json().get(RTables.JSON_TOURNAMENT(self.code), Path(key))
