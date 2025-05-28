import random
import re
import time
import traceback
from queue import Queue, Empty

from apps.client.models import Clients
from apps.game.models import Game
from apps.player.models import Player
from apps.tournaments.models import Tournaments
from utils.enums import GameStatus, ResponseError, RTables, EventType
from utils.threads.game import GameThread
from utils.threads.threads import Threads
from utils.threads.tournament import TournamentThread
from utils.websockets.channel_send import send_group_error

tournament_queue = Queue()
local_queue = Queue()

class MatchmakingThread(Threads):
    def __init__(self, name):
        super().__init__(name)
        self.tournament = None
        self.local = None

    def main(self):
        self.tournament: Tournaments = None
        game: Game = Game.create_game(runtime=True)

        while not self._stop_event.is_set():
            try:
                if self.check_tournament():
                    TournamentThread(self.tournament).start()

                if self.check_local():
                    game = self.local

                if game is None:
                    game = Game.create_game(runtime=True)

                if self.select_players(game) or game.local:
                    game.create_redis_game()
                    game.rset_status(GameStatus.MATCHMAKING)
                    
                    if not game.init_players():
                        self._logger.error("Salut la team on est la")
                        GameThread(game=game).cleanup()
                        if game.local:
                            self.redis.hdel(RTables.HASH_LOCAL_QUEUE, str(game.pL.client.id))
                        game = None
                        continue

                    game.rset_status(GameStatus.STARTING)
                    GameThread(game=game).start()
                    game = None

                time.sleep(1)

            except Exception as e:
                self._logger.error(traceback.format_exc())
                if game:
                    game.error_game()
                if game.pL:
                    send_group_error(RTables.GROUP_CLIENT(game.pL.id), ResponseError.MATCHMAKING_ERROR)
                    game.pL.leave_queue(game.code, game.is_duel, game.local)
                if game.pR:
                    send_group_error(RTables.GROUP_CLIENT(game.pR.id), ResponseError.MATCHMAKING_ERROR)
                    game.pR.leave_queue(game.code, game.is_duel, game.local)

    def cleanup(self):
        game_keys = self.redis.keys('game:*')
        for key in game_keys:
            self.redis.delete(key)

        # self.redis.delete(RTables.HASH_CLIENT)
        self.redis.delete(RTables.HASH_G_QUEUE)
        self.redis.delete(RTables.HASH_DUEL_QUEUE('*'))
        self.redis.delete(RTables.HASH_TOURNAMENT_QUEUE('*'))
        self.redis.delete(RTables.HASH_MATCHES)

        # RedisConnectionPool.close_connection(self.__class__.__name__)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def check_tournament(self) -> Tournaments:
        try:
            self.tournament = tournament_queue.get_nowait()
            return True
        except Empty:
            return False

    def check_local(self) -> Tournaments:
        try:
            self.local = local_queue.get_nowait()
            return True
        except Empty:
            return False

    def select_global(self, game):
        clients_queue = self.redis.hgetall(RTables.HASH_G_QUEUE)
        clients = [Clients.get_client_by_id(client.decode('utf-8')) for client in clients_queue]
        if len(clients) >= 2:
            selected_clients = clients[:2]  # this gets the first 2 players of the list
            random.shuffle(selected_clients)
            game.is_duel = False
            game.pL = Player.create_player(selected_clients[0])
            game.pR = Player.create_player(selected_clients[1])
            if game.pL is not None and game.pR is not None:
                return True
        return False

    def select_duel(self, game):
        for duel in self.redis.scan_iter(RTables.HASH_DUEL_QUEUE('*')):
            clients = list(self.redis.hgetall(duel).items())
            if len(clients) >= 2:
                random.shuffle(clients)
                client_1 = clients[0][0].decode('utf-8')
                client_2 = clients[1][0].decode('utf-8')
                stat_p1 = clients[0][1].decode('utf-8')
                stat_p2 = clients[1][1].decode('utf-8')

                client_id_1 = Clients.get_client_by_id(client_1)
                client_id_2 = Clients.get_client_by_id(client_2)
                channel_p1 = self.redis.hget(name=RTables.HASH_CLIENT(client_id_1.id), key=str(EventType.GAME.value))
                channel_p2 = self.redis.hget(name=RTables.HASH_CLIENT(client_id_2.id), key=str(EventType.GAME.value))
                if not channel_p1 or not channel_p2:
                    return False
                if stat_p1 == 'True' and stat_p2 == 'True':
                    game.is_duel = True
                    game.code = re.search(rf'{RTables.HASH_DUEL_QUEUE("")}(\w+)$', duel.decode('utf-8')).group(1)
                    game.game_key = RTables.JSON_GAME(game.code)
                    game.pL = Player.create_player(client_id_1)
                    game.pR = Player.create_player(client_id_2)
                    return True
        return False

    def select_local(self, game):
        for local_client in self.redis.hgetall(RTables.HASH_LOCAL_QUEUE):
            client = Clients.get_client_by_id(local_client.decode('utf-8'))
            game.local = True
            game.pL = Player.create_player(client)
            game.pR = Player.create_player(client)
            return True
        return False

    def select_players(self, game):
        # First we check the global queue
        if self.select_global(game):
            return True
        if self.select_duel(game):
            return True
        # if self.select_local(game):
        #     return True
        return False
