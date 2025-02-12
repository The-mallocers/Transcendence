import asyncio
import random
import time
from typing import Dict

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from apps.player.models import Player
from apps.pong.api.serializers import BallSerializer
from apps.pong.utils import GameState
from apps.shared.models import Clients
from utils.pong.enums import RequestType
from utils.pong.objects import FPS, Ball, CANVAS_HEIGHT, CANVAS_WIDTH, \
    BALL_SPEED


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

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ HANDLES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #



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

