import time
import traceback
from apps.client.models import Clients
from apps.tournaments.models import Tournaments
from utils.enums import EventType, GameStatus, RTables, ResponseAction, ResponseError
from utils.redis import RedisConnectionPool
from utils.threads.threads import Threads
from utils.util import create_tournament_id
from utils.websockets.channel_send import asend_group, send_group, send_group_error
from redis.commands.json.path import Path
from utils.serializers.tournament_redis_start import TournamentArgsSerializer


# This thread wil :
# Manage the lobby and make sure everybody is in when the tournament is starting
# Do the match matchmaking for the tournament, take players as they go and match them against one another.
# After the tournament is over, clean up redis and destroy itself.
# {
#     "event": "tournament",
#     "data": {
#         "action": "create_tournament",
#         "args": {
#             "name": "Mon tournoi",
#             "max_players": 8,
#             "public": true,
#             "bots": true,
#             "points_to_win": 11,
#             "timer": 120
#         }
#     }
# }



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
        self.create_tournament_redis()
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
        
    def create_tournament_redis(self):
        data = self.get_valid_data()
        if data == None:
            pass
            #Throw exception ? Idk
        else:
            pass
            #Upload data to redis. The only data missing are the players and we will update this as we go.
        pass 

    #returns None if the data isnt valid, but feel free to change the error handling
    def get_valid_data(self) -> dict:
        data = {
            "id": self.code,
            "host": self.host, #Im not quite sure what assigning a class will return
            "max_players": self.max_player,
            "name": self.title, #should this be name or title ?
            "public": self.public,
            "bots": self.bots,
            "points_to_win": self.points_to_win,
            "timer": self.timer
        }
        serializer = TournamentArgsSerializer(data=data) 
        if serializer.is_valid():
            return serializer.data
        else:
            self._logger.warning(f"Serializer errors: {serializer.errors}")
            return None