from json import JSONDecodeError, loads
import traceback

from utils.enums import EventType, ResponseError, RTables
from utils.websockets.channel_send import asend_group_error
from utils.websockets.consumers.consumer import WsConsumer
from utils.websockets.services.game import GameService
from utils.websockets.services.matchmaking import MatchmakingService
from utils.websockets.services.services import ServiceError

class GameConsumer(WsConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = MatchmakingService()

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = loads(text_data)
            if self.event_type is EventType.MATCHMAKING and data['event'] == EventType.GAME.value:
                self.event_type = EventType(data['event'])
                self.service = GameService()

            if data['event'] == EventType.GAME.value and await self._redis.hget(name=RTables.HASH_MATCHES, key=str(self.client.id)) is None:
                raise ServiceError('You are not in game')
            return await super().receive(text_data, bytes_data)

        except ServiceError as e:
            await asend_group_error(RTables.GROUP_CLIENT(self.client.id), ResponseError.NO_GAME, str(e))

        except JSONDecodeError as e:
            self._logger.error(f'Json error: {e}')
            await asend_group_error(RTables.GROUP_CLIENT(self.client.id), ResponseError.JSON_ERROR)

    async def connect(self):
        await super().connect()
        alreadyInGame = await self.is_client_in_game(str(self.client.id))
        if alreadyInGame:
            await asend_group_error(
                    RTables.GROUP_CLIENT(self.client.id), 
                    ResponseError.ALREAY_IN_GAME, 
                    content=f"You are already in game",
                    close=True
                )
            await self.close(code=4001)  # Custom close code for "already in game"
            return False




    async def is_client_in_game(self, client_id: str) -> bool:
        try:
            game_keys = await self._redis.keys("game_*")
            
            for game_key in game_keys:
                try:
                    result = await self._redis.execute_command(
                        'JSON.GET', 
                        game_key, 
                        '$[?(@.player_left.id == "' + client_id + '" || @.player_right.id == "' + client_id + '")]'
                    )
                    if result and result != '[]':  
                        return True
                except Exception as e:
                    self._logger.warning(f"Error checking game {game_key}: {e}")
                    continue
                    
            return False
            
        except Exception as e:
            self._logger.error(f"Error checking if client {client_id} is in game: {e}")
            return False