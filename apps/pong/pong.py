import asyncio
import logging
import random
import time

from apps.pong.api.serializers import PaddleSerializer, BallSerializer
from utils.pong.enums import EventType, ResponseAction
from utils.pong.objects import FPS, CANVAS_HEIGHT, CANVAS_WIDTH, BALL_SPEED, OFFSET_PADDLE, PADDLE_HEIGHT, PADDLE_WIDTH
from utils.pong.objects.ball import Ball
from utils.pong.objects.objects_state import GameState
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score
from utils.websockets.channel_send import send_group
from utils.pong.enums import PaddleMove


class PongLogic:
    def __init__(self, game_id, ball, paddle_pL, paddle_pR, score_pL, score_pR):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.last_update: float = time.time()
        self.game_id = game_id

        # ── Objects ───────────────────────────────────────────────────────────────────
        self.ball: Ball = ball
        self.paddle_pL: Paddle = paddle_pL
        self.paddle_pR: Paddle = paddle_pR
        self.score_pL: Score = score_pL
        self.score_pR: Score = score_pR


    async def game_task(self):
        try:
            # Regular game update logic
            previous_state = GameState.create_copy(self)
            await self._game_loop()
            current_state = GameState.create_copy(self)
            changes = GameState.get_differences(current_state, previous_state)
            await self._game_update(changes)
            await asyncio.sleep(1 / FPS) #Toy with this variable.
        except asyncio.CancelledError:
            pass
    async def handle_wall_collision(self, y) -> float:
        height = await self.get_height()
        if y <= 0:
            return 0    
        elif y + height >= CANVAS_HEIGHT:
            return CANVAS_HEIGHT - height
        else:
            return y


    async def _game_loop(self):
        current_time = time.time()
        delta_time = current_time - self.last_update

        await self.ball.multiply_dx(1.001)
        await self.ball.multiply_dy(1.001)

        await self.ball.increase_x(await self.ball.get_dx() * delta_time)
        await self.ball.increase_y(await self.ball.get_dy() * delta_time)

        if (await self.paddle_pL.get_move() == PaddleMove.UP):
            await self.paddle_pL.increase_y(delta_time)
        elif (await self.paddle_pL.get_move() == PaddleMove.DOWN):
            await self.paddle_pL.decrease_y(delta_time)

        if (await self.paddle_pR.get_move() == PaddleMove.UP):
            await self.paddle_pR.increase_y(delta_time)
        elif (await self.paddle_pR.get_move() == PaddleMove.DOWN):
            await self.paddle_pR.decrease_y(delta_time)

        if (await self.paddle_pR.get_move() == PaddleMove.IDLE):
            pass
        elif (await self.paddle_pR.get_move() == PaddleMove.IDLE):
            pass
        

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
                await self.ball.get_x() - await self.ball.get_radius() <= await self.paddle_pL.get_x() + await self.paddle_pL.get_width() and
                await self.ball.get_x() >= await self.paddle_pL.get_x() and
                await self.ball.get_y() >= await self.paddle_pL.get_y() and
                await self.ball.get_y() <= await self.paddle_pL.get_y() + await self.paddle_pL.get_height()):
            await self.ball.set_dx(abs(await self.ball.get_dx()))  # Ensure ball moves right
            await self.ball.set_x(
                await self.paddle_pL.get_x() + await self.paddle_pL.get_width() + await self.ball.get_radius())

        # Right paddle collision
        if (await self.ball.get_x() + await self.ball.get_radius() >= await self.paddle_pR.get_x() and
                await self.ball.get_x() <= await self.paddle_pR.get_x() + await self.paddle_pR.get_width() and
                await self.ball.get_y() >= await self.paddle_pR.get_y() and
                await self.ball.get_y() <= await self.paddle_pR.get_y() + await self.paddle_pR.get_height()):
            await self.ball.set_dx(-abs(await self.ball.get_dx()))  # Ensure ball moves left
            await self.ball.set_x(await self.paddle_pR.get_x() - await self.ball.get_radius())

        # Scoring
        if await self.ball.get_x() <= 0:
            await self.score_pL.add_score()
            await self._reset_ball(self.ball)
        elif await self.ball.get_x() >= CANVAS_WIDTH:
            await self.score_pR.add_score()
            await self._reset_ball(self.ball)

        await self.ball.update()
        await self.paddle_pL.update()
        await self.paddle_pR.update()
        await self.score_pL.update()
        await self.score_pR.update()

        self.last_update = current_time

    async def _game_update(self, changes):
        # self._logger.info(changes)
        if changes['ball']:
            await self.ball.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.BALL_UPDATE, BallSerializer(self.ball).data)

        if changes['paddle_pL']:
            await self.paddle_pL.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.PADDLE_LEFT_UPDATE,
                             PaddleSerializer(self.paddle_pL).data)

        if changes['paddle_pR']:
            await self.paddle_pR.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.PADDLE_RIGHT_UPDATE,
                             PaddleSerializer(self.paddle_pR).data)

        if changes['score_pL']:
            await self.score_pL.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.SCORE_LEFT_UPDATE,
                             await self.score_pL.get_score())

        if changes['score_pR']:
            await self.score_pR.update()
            await send_group(self.game_id, EventType.UPDATE, ResponseAction.SCORE_RIGHT_UPDATE,
                             await self.score_pR.get_score())

    async def _reset_ball(self, ball):
        await ball.set_x(CANVAS_WIDTH / 2)
        await ball.set_y(CANVAS_HEIGHT / 2)
        await ball.set_dx(BALL_SPEED * (1 if random.random() > 0.5 else -1))
        await ball.set_dy(BALL_SPEED * (1 if random.random() > 0.5 else -1))