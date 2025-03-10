import asyncio
import logging
import random
import time

from apps.pong.api.serializers import PaddleSerializer, BallSerializer
from utils.pong.enums import EventType, ResponseAction
from utils.pong.objects import FPS, CANVAS_HEIGHT, CANVAS_WIDTH, BALL_SPEED
from utils.pong.objects.ball import Ball
from utils.pong.objects.objects_state import GameState
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score
from utils.websockets.channel_send import send_group


class PongLogic:
    def __init__(self, game_id, ball, paddle_p1, paddle_p2, score_p1, score_p2):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.last_update: float = time.time()
        self.game_id = game_id

        # ── Objects ───────────────────────────────────────────────────────────────────
        self.ball: Ball = ball
        self.paddle_p1: Paddle = paddle_p1
        self.paddle_p2: Paddle = paddle_p2
        self.score_p1: Score = score_p1
        self.score_p2: Score = score_p2

    async def game_task(self):
        try:
            previous_state = GameState.create_copy(self)
            await self._game_loop()
            current_state = GameState.create_copy(self)

            changes = GameState.get_differences(current_state, previous_state)

            await self._game_update(changes)
            # await asyncio.sleep(1 / FPS)
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def _game_loop(self):
        current_time = time.time()
        delta_time = current_time - self.last_update

        await self.ball.multiply_dx(1.001)
        await self.ball.multiply_dy(1.001)

        await self.ball.increase_x(await self.ball.get_dx() * delta_time * FPS)
        await self.ball.increase_y(await self.ball.get_dy() * delta_time * FPS)

        # Ball collision with top and bottom walls
        if await self.ball.get_y() <= await self.ball.get_radius() or await self.ball.get_y() >= CANVAS_HEIGHT - await self.ball.get_radius():
            if await self.ball.get_y() < await self.ball.get_radius():
                await self.ball.set_y(await self.ball.get_radius())  # Correct ball position
            elif await self.ball.get_y() > CANVAS_HEIGHT - await self.ball.get_radius():
                await self.ball.set_y(CANVAS_HEIGHT - await self.ball.get_radius())  # Correct ball position
            # Reverse ball's vertical direction
            await self.ball.set_dy(await self.ball.get_dy() * -1)

        # Left paddle collision
        if (
                await self.ball.get_x() - await self.ball.get_radius() <= await self.paddle_p1.get_x() + await self.paddle_p1.get_width() and
                await self.ball.get_x() >= await self.paddle_p1.get_x() and
                await self.ball.get_y() >= await self.paddle_p1.get_y() and
                await self.ball.get_y() <= await self.paddle_p1.get_y() + await self.paddle_p1.get_height()):
            await self.ball.set_dx(abs(await self.ball.get_dx()))  # Ensure ball moves right
            await self.ball.set_x(
                await self.paddle_p1.get_x() + await self.paddle_p1.get_width() + await self.ball.get_radius())

        # Right paddle collision
        if (await self.ball.get_x() + await self.ball.get_radius() >= await self.paddle_p2.get_x() and
                await self.ball.get_x() <= await self.paddle_p2.get_x() + await self.paddle_p2.get_width() and
                await self.ball.get_y() >= await self.paddle_p2.get_y() and
                await self.ball.get_y() <= await self.paddle_p2.get_y() + await self.paddle_p2.get_height()):
            await self.ball.set_dx(-abs(await self.ball.get_dx()))  # Ensure ball moves left
            await self.ball.set_x(await self.paddle_p2.get_x() - await self.ball.get_radius())

        # Scoring
        if await self.ball.get_x() <= 0:
            await self.score_p1.add_score()
            await self._reset_ball(self.ball)
        elif await self.ball.get_x() >= CANVAS_WIDTH:
            await self.score_p2.add_score()
            await self._reset_ball(self.ball)

        await self.ball.update()
        await self.paddle_p1.update()
        await self.paddle_p2.update()
        await self.score_p1.update()
        await self.score_p2.update()

        self.last_update = current_time

    async def _game_update(self, changes):
        if changes['ball']:
            await self.ball.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.BALL_UPDATE, BallSerializer(self.ball).data)

        if changes['paddle_p1']:
            await self.paddle_p1.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.PADDLE_1_UPDATE, PaddleSerializer(self.paddle_p1).data)

        if changes['paddle_p2']:
            await self.paddle_p2.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.PADDLE_2_UPDATE, PaddleSerializer(self.paddle_p2).data)

        if changes['score_p1']:
            await self.score_p1.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.SCORE_1_UPDATE, await self.score_p1.get_score())

        if changes['score_p2']:
            await self.score_p2.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.SCORE_2_UPDATE, await self.score_p2.get_score())

    async def _reset_ball(self, ball):
        await ball.set_x(CANVAS_WIDTH / 2)
        await ball.set_y(CANVAS_HEIGHT / 2)
        await ball.set_dx(BALL_SPEED * (1 if random.random() > 0.5 else -1))
        await ball.set_dy(BALL_SPEED * (1 if random.random() > 0.5 else -1))