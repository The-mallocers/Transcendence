import asyncio
import random
import time
from typing import Dict

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from apps.player.api.serializers import PlayerSerializer
from apps.player.models import Player
from apps.pong.api.serializers import BallSerializer, PaddleSerializer
from apps.pong.utils import RequestType, GameState, ErrorType, Paddle, FPS, \
    Ball, CANVAS_HEIGHT, CANVAS_WIDTH, BALL_SPEED
from apps.shared.models import Clients


class PongLogic:
    games: Dict[str, GameState] = {}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ DATABASE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    @database_sync_to_async
    def check_room_exists(self, player_id):
        try:
            Player.objects.get(id=player_id)
            return True
        except Player.DoesNotExist:
            return False

    @database_sync_to_async
    def get_player(self, client_id):
        try:
            client = Clients.objects.get(id=client_id)
            return client.player
        except (Clients.DoesNotExist | Player.DoesNotExist):
            return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ LOGIC ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def process_action(self, client_id, data: Dict, room: str):
        request_type: RequestType = RequestType(data.get('action'))
        player = await self.get_player(client_id)
        handlers = {
            RequestType.JOIN_GAME: self._handle_join_game,
            RequestType.PADDLE_MOVE: self._handle_paddle_move,
            RequestType.START_GAME: self._handle_start_game,
            RequestType.IS_READY: self._handle_is_ready,
        }

        if room not in PongLogic.games:
            PongLogic.games[room] = GameState(id=room)
        if not player:
            raise ValueError(f'Unknown client: {client_id}')
        if request_type in handlers:
            return await handlers[request_type](data, PongLogic.games[room], player)
        else:
            raise ValueError(f'Unknown action: {request_type}')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ HANDLES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def _handle_join_game(self, data: Dict, game: GameState, player: Player):
        #Check if the player is arleady join
        if player == game.player_1 or player == game.player_2:
            return {
                'error': ErrorType.ALREADY_JOIN,
                'player_id': str(player.id)
            }
        else: #il faudra implementer le random pour savoir sur quel cote le joueur joue
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

        return {
            'type': RequestType.JOIN_GAME,
            'player_id': str(player.id)
        }

    async def _handle_paddle_move(self, data: Dict, game: GameState, player: Player):
        if player == game.player_1 or player == game.player_2:
            await player.move(data.get('direction'))
            return {
                'type': RequestType.PADDLE_MOVE,
                'player_id': player.id,
                'paddle': PaddleSerializer(player.paddle).data
            }
        else:
            return {
                'error': ErrorType.NOT_IN_GAME,
                'player_id': str(player.id)
            }

    async def _handel_is_ready(self, data: Dict, game: GameState, player: Player):
        if player == game.player_1 or player == game.player_2:
            player.is_ready = True
            return {
                'type': RequestType.IS_READY,
                'player_id': player.id,
                'is_ready': player.is_ready
            }

    async def _handle_start_game(self, data: Dict, game: GameState, player: Player):
        if game.player_1.is_ready and game.player_2.is_ready:
            game.active = True
            game.task = asyncio.create_task(self._game_task(game))
            return {
                'type': RequestType.START_GAME,
            }
        else:
            return {
                'error': ErrorType.NOT_READY
            }

    async def handle_disconnect(self, room: str, player_id: str):
        if room in self.game_states and player_id in \
                self.game_states[room]['players']:
            self.game_states[room]['players'][player_id].is_active = False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ LOOP LOGIC ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    async def _game_task(self, game: GameState):
        try:
            while game.active:
                previous_state = game.get_snapshot()
                self._game_loop(game)
                current_state = game.get_snapshot()

                changes = {
                    key: (previous_state[key], current_state[key])
                    for key in previous_state
                    if previous_state[key] != current_state[key]
                }

                await self._game_update(game, changes)
                await asyncio.sleep(1/ FPS)
        except asyncio.CancelledError:
            pass

    def _game_loop(self, game: GameState):
        current_time = time.time()
        delta_time = current_time - game.last_update
        ball: Ball = game.ball

        ball.dx *= 1.001
        ball.dy *= 1.001

        ball.x += ball.dx * delta_time * FPS
        ball.y += ball.dy * delta_time * FPS

        # # Wall bounces (with akward code otherwise ball get stuck to wall sometimes)
        if ball.y <= ball.radius or ball.y >= CANVAS_HEIGHT - ball.radius:
            if ball.y < ball.radius:
                ball.y = ball.radius
            elif ball.y > CANVAS_HEIGHT - ball.radius:
                ball.y = CANVAS_HEIGHT - ball.radius
            ball.dy *= -1

        paddle_p1 = game.player_1.paddle
        paddle_p2 = game.player_2.paddle

        # Left paddle collision
        if (ball.x - ball.radius <= paddle_p1.x + paddle_p1.width and
            ball.x >= paddle_p1.x and
            ball.y >= paddle_p1.y and
            ball.y <= paddle_p1.y + paddle_p1.height):
            ball.dx = abs(ball.dx)  # Ensure ball moves right
            ball.x = paddle_p1.x + paddle_p1.width + ball.radius

        # Right paddle collision
        if (ball.x + ball.radius >= paddle_p2.x and
            ball.x <= paddle_p2.x + paddle_p2.width and
            ball.y >= paddle_p2.y and
            ball.y <= paddle_p2.y + paddle_p2.height):
            ball.dx = -abs(ball.dx)  # Ensure ball moves left
            ball.x = paddle_p2.x - ball.radius

        # Scoring
        if ball.x <= 0:
            game.player_1.score += 1
            self._reset_ball(ball)
        elif ball.x >= CANVAS_WIDTH:
            game.player_2.score += 1
            self._reset_ball(ball)

        game.last_update = current_time

    async def _game_update(self, game: GameState, changes: dict):
        if not changes:
            return

        channel_layer = get_channel_layer()

        for key, (old, new) in changes.items():
            if key == 'ball':
                await channel_layer.group_send(f"group_{game.id}", {
                    'type': 'game_message',
                    'message': {
                        'type': RequestType.BALL_UPDATE,
                        'ball': BallSerializer(game.ball).data
                    }
                })
            elif key == 'p1_score':
                await channel_layer.group_send(f"group_{game.id}", {
                    'type': 'game_message',
                    'message': {
                        'type': RequestType.P1_SCORE_UPDATE,
                        'score': game.player_1.score
                    }
                })
            elif key == 'p2_score':
                await channel_layer.group_send(f"group_{game.id}", {
                    'type': 'game_message',
                    'message': {
                        'type': RequestType.P2_SCORE_UPDATE,
                        'score': game.player_2.score
                    }
                })

    def _reset_ball(self, ball: Ball):
        ball.x = CANVAS_WIDTH / 2
        ball.y = CANVAS_HEIGHT / 2
        ball.dx = BALL_SPEED * ( 1 if random.random() > 0.5 else -1)
        ball.dy = BALL_SPEED * ( 1 if random.random() > 0.5 else -1)

