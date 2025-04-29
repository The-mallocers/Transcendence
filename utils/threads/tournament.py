import random
import traceback
from time import sleep

from asgiref.sync import sync_to_async
from redis.commands.json.path import Path

from apps.client.models import Clients
from apps.game.models import Game
from apps.player.models import Player
from utils.enums import EventType, GameStatus, RTables, ResponseAction, ResponseError, TournamentStatus
from utils.serializers.tournament import TournamentSerializer
from utils.threads.game import GameThread
from utils.threads.threads import Threads
from utils.util import create_tournament_id
from utils.websockets.channel_send import send_group, send_group_error


class TournamentThread(Threads):
    def __init__(self, host, code):
        # Init
        self.code = code
        super().__init__(f'TournamentThread[{self.code}]')

        # Tournaments settings
        self.host: Clients = host
        self.clients: list[Clients] = [host]
        self.max_players = self.get('max_players')
        self.title = self.get('title')
        self.public = self.get('public')
        self.bots = self.get('bots')
        self.points_to_win = self.get('points_to_win')
        self.timer = self.get('timer')
        self.status: TournamentStatus = TournamentStatus(self.get('status'))

        self.rounds = self.get('scoreboards.num_rounds')
        self.set('scoreboards.current_round', 1)
        self.current_round = self.get('scoreboards.current_round')
        self.game_num = int(self.max_players - 1)
        self.games: list[Game] = self.create_games()

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
            send_group_error(RTables.GROUP_TOURNAMENT(self.code), ResponseError.EXCEPTION, str(e), close=True)
        finally:
            self.stop()

    def cleanup(self):
        for game in self.games:
            self.redis.delete(RTables.JSON_GAME(game.code))
        self.redis.delete(RTables.JSON_TOURNAMENT(self.code))
        self.redis.expire(f'channels:group:{RTables.GROUP_TOURNAMENT(self.code)}', 0)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ EVENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def _waitting(self):
        if self.status is TournamentStatus.WAITING:
            queue = self.redis.hgetall(RTables.HASH_TOURNAMENT_QUEUE(self.code))

            for client_id_bytes, ready in queue.items():
                client_id = client_id_bytes.decode('utf-8')
                client = Clients.get_client_by_id(client_id)
                if client and client not in self.clients and ready.decode('utf-8') == 'True':
                    self.add_client(client_id)
                    send_group(RTables.GROUP_TOURNAMENT(self.code),
                               EventType.TOURNAMENT,
                               ResponseAction.TOURNAMENT_PLAYER_JOIN,
                               {'id': client_id})

            if len(queue) >= self.max_players:
                self.set_status(TournamentStatus.CREATING_MATCH)
                send_group(RTables.GROUP_TOURNAMENT(self.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_PLAYERS_READY)
                return True
        return False

    def _starting(self):
        if self.status is TournamentStatus.CREATING_MATCH:
            random.shuffle(self.clients)
            player = 0
            for game in range(0, int(self.max_players / 2)):  # on init uniquement le premier round
                self.games[game].pL = Player(str(self.clients[player].id))
                player += 1
                self.games[game].pR = Player(str(self.clients[player].id))
                player += 1
                self.games[game].init_players()
                self.games[game].rset_status(GameStatus.MATCHMAKING)
                send_group(RTables.HASH_CLIENT(self.games[game].pL.client_id), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_GAME_READY)
                send_group(RTables.HASH_CLIENT(self.games[game].pR.client_id), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_GAME_READY)
                GameThread(game=self.games[game]).start()
            self.set_status(TournamentStatus.RUNNING)
            return True
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

    def create_games(self) -> list[Game]:
        games: list[Game] = []
        for r in range(1, self.rounds + 1):
            matches_in_round = self.redis.json().get(RTables.JSON_TOURNAMENT(self.code), Path(f'scoreboards.rounds.round_{r}.matches_total'))
            for m in range(1, matches_in_round + 1):
                game = Game()
                game.tournament_code = self.code
                game.create_redis_game()
                game.rset_status(GameStatus.WAITING)
                games.append(game)
                self.redis.json().set(RTables.JSON_TOURNAMENT(self.code), Path(f'scoreboards.rounds.round_{r}.games.r{r}m{m}.game_code'),
                                      game.code)
        return games

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
            for field, errors in serializer.errors.items():
                for error in errors:
                    raise ValueError(f'{field}: {error}')

    def set_status(self, status: TournamentStatus):
        self.status = status
        self.redis.json().set(RTables.JSON_TOURNAMENT(self.code), Path('status'), status)

    def get(self, key):
        return self.redis.json().get(RTables.JSON_TOURNAMENT(self.code), Path(key))

    def set(self, key, value):
        self.redis.json().set(RTables.JSON_TOURNAMENT(self.code), Path(key), value)

    def add_client(self, client_id):
        client = Clients.get_client_by_id(client_id)
        self.clients.append(client)
        self.redis.json().set(RTables.JSON_TOURNAMENT(self.code), Path('clients'), Clients.get_id_list(self.clients))
