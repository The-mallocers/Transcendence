import asyncio
import logging
import random
import time

from apps.game.models import Game
from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer, BallSerializer
from apps.shared.models import Clients
from utils.pong.enums import EventType, ResponseAction
from utils.pong.enums import GameStatus
from utils.pong.enums import PaddleMove
from utils.pong.objects import FPS, CANVAS_HEIGHT, CANVAS_WIDTH, BALL_SPEED, OFFSET_PADDLE, PADDLE_WIDTH
from utils.pong.objects.ball import Ball
from utils.pong.objects.objects_state import GameState
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score
from utils.websockets.channel_send import send_group


class PongLogic:
    def __init__(self, game: Game, redis):  # ball, paddle_pL, paddle_pR, score_pL, score_pR):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.redis = redis
        self.game = game
        self.game_id = game.game_id
        self.last_update: float = -1  # This hack is sponsored by tfreydie and prevents the random +1 score at the start

        # ── Objects ───────────────────────────────────────────────────────────────────
        self.ball: Ball = Ball(game_id=self.game_id, redis=redis)
        self.paddle_pL: Paddle = Paddle(game_id=self.game_id, redis=redis, player_id=self.game.pL.client_id,
                                        x=OFFSET_PADDLE)
        self.paddle_pR: Paddle = Paddle(game_id=self.game_id, redis=redis, player_id=self.game.pR.client_id,
                                        x=CANVAS_WIDTH - OFFSET_PADDLE - PADDLE_WIDTH)
        self.score_pL: Score = Score(game_id=self.game_id, redis=redis, player_id=self.game.pL.client_id)
        self.score_pR: Score = Score(game_id=self.game_id, redis=redis, player_id=self.game.pR.client_id)
        self.points_to_win = self.game.points_to_win

    def game_task(self):
        try:
            # Regular game update logic
            previous_state = GameState.create_copy(self)
            self._game_loop()
            current_state = GameState.create_copy(self)
            changes = GameState.get_differences(current_state, previous_state)
            self._game_update(changes)
            time.sleep(1 / FPS)  # Toy with this variable.
        except asyncio.CancelledError:
            pass

    def handle_paddle_direction(self, paddle, delta_time):
        move = paddle.get_move()
        if move == PaddleMove.UP:
            paddle.decrease_y(delta_time)
        elif move == PaddleMove.DOWN:
            paddle.increase_y(delta_time)
        elif move == PaddleMove.IDLE:
            # Maybe we'll do things when its idle later !
            pass

    def _game_loop(self):
        current_time = time.time()
        # ugly as shit fix but doing properly would require changing the way we are initializing a game.
        if self.last_update == -1:
            delta_time = 0
        else:
            delta_time = current_time - self.last_update

        self.ball.multiply_dx(1.001)
        self.ball.multiply_dy(1.001)

        self.ball.increase_x(self.ball.get_dx() * delta_time)
        self.ball.increase_y(self.ball.get_dy() * delta_time)

        self.handle_paddle_direction(self.paddle_pL, delta_time)
        self.handle_paddle_direction(self.paddle_pR, delta_time)

        # Ball collision with top and bottom walls
        if self.ball.get_y() <= self.ball.get_radius() or self.ball.get_y() >= CANVAS_HEIGHT - self.ball.get_radius():
            if self.ball.get_y() < self.ball.get_radius():
                self.ball.set_y(self.ball.get_radius())  # Correct ball position
            elif self.ball.get_y() > CANVAS_HEIGHT - self.ball.get_radius():
                self.ball.set_y(CANVAS_HEIGHT - self.ball.get_radius())  # Correct ball position
            # Reverse ball's vertical direction
            self.ball.set_dy(self.ball.get_dy() * -1)

        # Left paddle collision
        if (
                self.ball.get_x() - self.ball.get_radius() <= self.paddle_pL.get_x() + self.paddle_pL.get_width() and
                self.ball.get_x() >= self.paddle_pL.get_x() and
                self.ball.get_y() >= self.paddle_pL.get_y() and
                self.ball.get_y() <= self.paddle_pL.get_y() + self.paddle_pL.get_height()):
            self.ball.set_dx(abs(self.ball.get_dx()))  # Ensure ball moves right
            self.ball.set_x(
                self.paddle_pL.get_x() + self.paddle_pL.get_width() + self.ball.get_radius())

        # Right paddle collision
        if (self.ball.get_x() + self.ball.get_radius() >= self.paddle_pR.get_x() and
                self.ball.get_x() <= self.paddle_pR.get_x() + self.paddle_pR.get_width() and
                self.ball.get_y() >= self.paddle_pR.get_y() and
                self.ball.get_y() <= self.paddle_pR.get_y() + self.paddle_pR.get_height()):
            self.ball.set_dx(-abs(self.ball.get_dx()))  # Ensure ball moves left
            self.ball.set_x(self.paddle_pR.get_x() - self.ball.get_radius())

        # Scoring
        if self.ball.get_x() <= 0:
            self.score_pR.add_score()
            self._reset_ball(self.ball)
        elif self.ball.get_x() >= CANVAS_WIDTH:
            self.score_pL.add_score()
            self._reset_ball(self.ball)

        # Check win
        if self.score_pL.get_score() >= self.points_to_win:
            self.game.rset_status(GameStatus.ENDING)
        elif self.score_pR.get_score() >= self.points_to_win:
            self.game.rset_status(GameStatus.ENDING)

        self.ball.update()
        self.paddle_pL.update()
        self.paddle_pR.update()
        self.score_pL.update()
        self.score_pR.update()

        self.last_update = current_time

    def _game_update(self, changes):
        if changes['ball']:
            self.ball.update()
            send_group(self.game_id, EventType.UPDATE, ResponseAction.BALL_UPDATE, BallSerializer(self.ball).data)

        if changes['paddle_pL']:
            self.paddle_pL.update()
            send_group(self.game_id, EventType.UPDATE, ResponseAction.PADDLE_LEFT_UPDATE,
                       PaddleSerializer(self.paddle_pL).data)

        if changes['paddle_pR']:
            self.paddle_pR.update()
            send_group(self.game_id, EventType.UPDATE, ResponseAction.PADDLE_RIGHT_UPDATE,
                       PaddleSerializer(self.paddle_pR).data)

        if changes['score_pL']:
            self.score_pL.update()
            send_group(self.game_id, EventType.UPDATE, ResponseAction.SCORE_LEFT_UPDATE,
                       self.score_pL.get_score())

        if changes['score_pR']:
            self.score_pR.update()
            send_group(self.game_id, EventType.UPDATE, ResponseAction.SCORE_RIGHT_UPDATE,
                       self.score_pR.get_score())

    def _reset_ball(self, ball):
        ball.set_x(CANVAS_WIDTH / 2)
        ball.set_y(CANVAS_HEIGHT / ((random.random() + 1) * 2))
        ball.set_dx(BALL_SPEED * (1 if random.random() > 0.5 else -1))
        ball.set_dy(BALL_SPEED * (1 if random.random() > 0.5 else -1))

    def set_result(self):
        if self.score_pL.get_score() > self.score_pR.get_score():
            winner = Player()
            winner.client = Clients.get_client_by_id(self.game.pL.client_id)
            winner.score = self.score_pL.get_score()
            winner.save()
            loser = Player()
            loser.client = Clients.get_client_by_id(self.game.pR.client_id)
            loser.score = self.score_pR.get_score()
            loser.save()
            # loser = Player.objects.create(client=Clients.get_client_by_id(self.game.pR.client_id), score=self.score_pR.get_score())
        elif self.score_pL.get_score() < self.score_pR.get_score():
            winner = Player()
            winner.client = Clients.get_client_by_id(self.game.pR.client_id)
            winner.score = self.score_pR.get_score()
            winner.save()
            loser = Player()
            loser.client = Clients.get_client_by_id(self.game.pL.client_id)
            loser.score = self.score_pL.get_score()
            loser.save()
            # winner = Player.objects.create(client=client, score=self.score_pR.get_score())
            # loser = Player.objects.create(client=Clients.get_client_by_id(self.game.pL.client_id), score=self.score_pL.get_score())
        finished_game = Game.objects.create(id=self.game.game_id, winner=winner, loser=loser,
                                            points_to_win=self.game.points_to_win)
        winner.game = finished_game
        winner.save()
        loser.game = finished_game
        loser.save()
        # winner.update(game=finished_game)
        # loser.update(game=finished_game)
