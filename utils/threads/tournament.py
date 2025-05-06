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
        self.current_round = self.get_current_round()
        self.game_num = int(self.max_players - 1)
        self.games: list[Game] = self.create_games()

    def main(self):
        try:
            self.set_status(TournamentStatus.WAITING)
            while self.is_running():
                if self._waitting():
                    sleep(2)
                if self._starting():
                    sleep(5)
                if self._running():
                    break

        except Exception as e:
            self._logger.error(traceback.format_exc())
            self.set_status(TournamentStatus.ERROR)
            send_group_error(RTables.GROUP_TOURNAMENT(self.code), ResponseError.EXCEPTION, str(e), close=True)
        finally:
            self.stoping()

    def cleanup(self):
        for game in self.games:
            if game.rget_status() is GameStatus.WAITING:
                self.redis.delete(RTables.JSON_GAME(game.code))
        # self.redis.delete(RTables.JSON_TOURNAMENT(self.code))
        self.redis.expire(f'channels:group:{RTables.GROUP_TOURNAMENT(self.code)}', 0)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ EVENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def _waitting(self):
        if self.status is TournamentStatus.WAITING:
            queue = self.redis.hgetall(RTables.HASH_TOURNAMENT_QUEUE(self.code))

            for client_id_bytes, ready in queue.items():
                client_id = client_id_bytes.decode('utf-8')
                client = Clients.get_client_by_id(client_id)
                if client and client not in self.clients and ready.decode('utf-8') == 'True':
                    self.add_client(client)
                    send_group(RTables.GROUP_TOURNAMENT(self.code),
                               EventType.TOURNAMENT,
                               ResponseAction.TOURNAMENT_PLAYER_JOIN,
                               {'id': str(client.id)})

            if len(queue) >= self.max_players:
                self.set_status(TournamentStatus.STARTING)
                send_group(RTables.GROUP_TOURNAMENT(self.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_PLAYERS_READY)
                return True
        return False

    def _starting(self):
        if self.status is TournamentStatus.STARTING:
            random.shuffle(self.clients)
            player = 0
            for game in self.games[:int(self.max_players / 2)]:  # get the first game for round 1
                game.pL = Player.create_player(self.clients[player])
                player += 1
                game.pR = Player.create_player(self.clients[player])
                player += 1
                game.init_players()
                game.rset_status(GameStatus.MATCHMAKING)
                send_group(RTables.HASH_CLIENT(game.pL.client.id), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_GAME_READY)
                send_group(RTables.HASH_CLIENT(game.pR.client.id), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_GAME_READY)
                GameThread(game=game).start()
            self.set_status(TournamentStatus.RUNNING)
            return True
        return False

    def _running(self):
        if self.status is TournamentStatus.RUNNING:

            if self.get_match_complete() == self.get_total_matches():
                self.set_current_round(self.get_current_round() + 1)
                self.place_players()
            else:
                self.manage_games()

            # if self.get_current_round() == self.rounds:
            #     return True
        return False

    def stoping(self):
        if self.status is TournamentStatus.ENDING:
            return True
        self.stop()
        return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ STATICS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
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

    @staticmethod
    def set_game_status(tournament_code, game_code: str, status: GameStatus, redis):
        rounds = redis.json().get(RTables.JSON_TOURNAMENT(tournament_code), Path('scoreboards.num_rounds'))
        if rounds is None:
            return None
        for r in range(1, rounds + 1):
            matches_in_round = redis.json().get(RTables.JSON_TOURNAMENT(tournament_code), Path(f'scoreboards.rounds.round_{r}.matches_total'))
            for m in range(1, matches_in_round + 1):
                game_id = redis.json().get(RTables.JSON_TOURNAMENT(tournament_code), Path(f'scoreboards.rounds.round_{r}.games.r{r}m{m}.game_code'))
                if game_id == game_code:
                    redis.json().set(RTables.JSON_TOURNAMENT(tournament_code), Path(f'scoreboards.rounds.round_{r}.games.r{r}m{m}.status'), status)
                    return

    @staticmethod
    def set_game_players(tournament_code, game_code: str, winner_id: str, loser_id: str, redis):
        rounds = redis.json().get(RTables.JSON_TOURNAMENT(tournament_code), Path('scoreboards.num_rounds'))
        if rounds is None:
            return None
        for r in range(1, rounds + 1):
            matches_in_round = redis.json().get(RTables.JSON_TOURNAMENT(tournament_code), Path(f'scoreboards.rounds.round_{r}.matches_total'))
            for m in range(1, matches_in_round + 1):
                game_id = redis.json().get(RTables.JSON_TOURNAMENT(tournament_code), Path(f'scoreboards.rounds.round_{r}.games.r{r}m{m}.game_code'))
                if game_id == game_code:
                    redis.json().set(RTables.JSON_TOURNAMENT(tournament_code), Path(f'scoreboards.rounds.round_{r}.games.r{r}m{m}.winner'), winner_id)
                    redis.json().set(RTables.JSON_TOURNAMENT(tournament_code), Path(f'scoreboards.rounds.round_{r}.games.r{r}m{m}.loser'), loser_id)
                    return

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    def create_games(self) -> list[Game]:
        games: list[Game] = []
        for r in range(1, self.rounds + 1):
            matches_in_round = self.redis.json().get(RTables.JSON_TOURNAMENT(self.code), Path(f'scoreboards.rounds.round_{r}.matches_total'))
            for m in range(1, matches_in_round + 1):
                game = Game.create_game(tournament_id=self.code)
                game.points_to_win = self.points_to_win
                game.create_redis_game()
                game.rset_status(GameStatus.WAITING)
                games.append(game)
                self.redis.json().set(RTables.JSON_TOURNAMENT(self.code), Path(f'scoreboards.rounds.round_{r}.games.r{r}m{m}.game_code'),
                                      game.code)
        return games

    def is_running(self) -> bool:
        self.status = TournamentStatus(self.redis.json().get(RTables.JSON_TOURNAMENT(self.code), Path('status')))
        if not self._stop_event.is_set() and self.status is not GameStatus.ERROR:
            return True
        if self.status is not TournamentStatus.RUNNING:
            host = self.redis.hexists(RTables.HASH_TOURNAMENT_QUEUE(self.code), str(self.host.id))
            if not host:
                send_group_error(RTables.GROUP_TOURNAMENT(self.code), ResponseError.HOST_LEAVE)
                return False
            return True
        else:
            return True

    def manage_games(self):
        for game in self.games[:self.get_total_matches()]:
            status = game.rget_status()
            if status is GameStatus.FINISHED:
                matches_completed = self.get(f'scoreboards.rounds.round_{self.get_current_round()}.matches_completed')
                self.set(f'scoreboards.rounds.round_{self.get_current_round()}.matches_completed', int(matches_completed) + 1)
                send_group(RTables.GROUP_TOURNAMENT(self.code), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_GAME_FINISH, {
                    'game_id': game.code,
                    'winner': str(game.winner.client.id),
                    'loser': str(game.loser.client.id)
                })
                send_group(RTables.GROUP_TOURNAMENT(game.loser.client.id), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_LOSE_GAME)
                self.del_client(game.loser.client)
                self.games.remove(game)
                break

    def place_players(self):
        for i, game in enumerate(self.games[:self.get_total_matches()]):
            previous_match_index = i * 2 + 1
            match_p1 = f'r{self.get_current_round() - 1}m{previous_match_index}'
            match_p2 = f'r{self.get_current_round() - 1}m{previous_match_index + 1}'
            client_1 = self.get_winner_match(self.get_current_round() - 1, match_p1)
            client_2 = self.get_winner_match(self.get_current_round() - 1, match_p2)
            game.pL = Player.create_player(client_1)
            game.pR = Player.create_player(client_2)
            game.init_players()
            game.rset_status(GameStatus.MATCHMAKING)
            send_group(RTables.HASH_CLIENT(game.pL.client.id), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_GAME_READY)
            send_group(RTables.HASH_CLIENT(game.pR.client.id), EventType.TOURNAMENT, ResponseAction.TOURNAMENT_GAME_READY)
            GameThread(game=game).start()

    # ━━ GETTER / SETTER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    # ── Setter ────────────────────────────────────────────────────────────────────── #

    def set(self, key, value):
        self.redis.json().set(RTables.JSON_TOURNAMENT(self.code), Path(key), value)
        
    def set_status(self, status: TournamentStatus):
        self.status = status
        self.set('status', status)

    def set_current_round(self, current_round):
        self.current_round = current_round
        self.set('scoreboards.current_round', current_round)

    # ── Getter ────────────────────────────────────────────────────────────────────── #
    
    def get(self, key):
        return self.redis.json().get(RTables.JSON_TOURNAMENT(self.code), Path(key))

    def get_current_round(self):
        return self.get('scoreboards.current_round')

    def get_total_matches(self):
        return self.get(f'scoreboards.rounds.round_{self.get_current_round()}.matches_total')

    def get_match_complete(self):
        return self.get(f'scoreboards.rounds.round_{self.get_current_round()}.matches_completed')

    def get_winner_match(self, rounds, game_id):
        match_code = self.get(f'scoreboards.rounds.round_{rounds}.games.{game_id}.game_code')
        game = Game.get_game_by_id(match_code)
        return game.winner

    # ── Adder / Deleter ────────────────────────────────────────────────────────────── #

    def del_client(self, client):
        self.clients.remove(client)
        self.redis.json().set(RTables.JSON_TOURNAMENT(self.code), Path('clients'), Clients.get_id_list(self.clients))

    def add_client(self, client):
        self.clients.append(client)
        self.redis.json().set(RTables.JSON_TOURNAMENT(self.code), Path('clients'), Clients.get_id_list(self.clients))
