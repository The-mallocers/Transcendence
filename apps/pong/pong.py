from typing import Dict

from asgiref.sync import sync_to_async

from apps.player.api.serializers import PlayerSerializer
from apps.player.models import Player
from apps.pong.utils import RequestType, GameState, ErrorType, Paddle



class PongLogic:
    games: Dict[str, GameState] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def process_action(self, action: RequestType, data: Dict, room: str):
        if room not in PongLogic.games:
            PongLogic.games[room] = GameState(id=room)

        handlers = {
            RequestType.JOIN_GAME: self._handle_join_game,
            RequestType.PADDLE_MOVE: self._handle_paddle_move,
            RequestType.GAME_STATE: self._handle_join_game,
            RequestType.PLAYER_ACTION: self._handle_join_game
        }

        if action in handlers:
            return await handlers[action](data, PongLogic.games[room])
        else:
            raise ValueError(f'Unknown action: {action}')

    async def _handle_join_game(self, data: Dict, game: GameState):
        player: Player = await sync_to_async(Player.objects.get, thread_sensitive=True)(id=data.get('player_id'))

        #Check if the player is arleady join
        if player == game.player_1 or player == game.player_2:
            return {
                'error': ErrorType.ALREADY_JOIN,
                'player_id': str(player.id)
            }
        else:
            if game.player_1 is None:
                player.position = 'right'
                game.player_1 = player
            elif game.player_2 is None:
                player.position = 'left'
                game.player_2 = player
            else:
                return {
                    'error': ErrorType.GAME_FULL,
                    'player_id': str(player.id)
                }
            await player.async_save()

        print(game)

        #Send to all the players, the player has joined
        return {
            'success': RequestType.JOIN_GAME,
            'player_id': str(player.id)
        }

    async def _handle_paddle_move(self, data: Dict, game: GameState):
        player: Player = await sync_to_async(Player.objects.get, thread_sensitive=True)(id=data.get('player_id'))

        if player == game.player_1 or player == game.player_2:
            await player.move(data.get('direction'))
            return {
                'success': RequestType.PADDLE_MOVE,
                'player': PlayerSerializer(player).data
            }
        else:
            return {
                'error': ErrorType.NOT_IN_GAME,
                'player_id': str(player.id)
            }
    #
    # async def _handle_player_action(self, data: Dict, room: str):
    #     player_id = data.get('player_id')
    #     action_type = data.get('action_type')
    #
    #     if player_id in self.game_states[room]['players']:
    #         player = self.game_states[room]['players'][player_id]
    #
    #         # Handle different types of player actions
    #         if action_type == 'attack':
    #             target_pos = Position(
    #                 data.get('target_x', 0),
    #                 data.get('target_y', 0)
    #             )
    #             # Add attack logic here
    #             return {
    #                 'action': 'player_attacked',
    #                 'player_id': player_id,
    #                 'target': target_pos.to_dict()
    #             }
    #
    #     return {'error': 'Invalid player action'}
    #
    # async def _handle_game_state(self, data: Dict, room: str):
    #     return {
    #         'action': 'game_state',
    #         'game_state': self._get_game_state_dict(room)
    #     }
    #
    # def _get_game_state_dict(self, room: str) -> Dict:
    #     state = self.game_states[room]
    #     return {
    #         'players': {
    #             pid: player.to_dict()
    #             for pid, player in state['players'].items()
    #         },
    #         'game_status': state['game_status']
    #     }

    async def handle_disconnect(self, room: str, player_id: str):
        if room in self.game_states and player_id in \
                self.game_states[room]['players']:
            self.game_states[room]['players'][player_id].is_active = False