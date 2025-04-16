import asyncio
import logging
import random
import time

from apps.client.models import Clients
from apps.game.models import Game
from apps.player.models import Player
from utils.enums import EventType, ResponseAction
from utils.enums import GameStatus
from utils.enums import PaddleMove
from utils.pong.objects import FPS, CANVAS_HEIGHT, CANVAS_WIDTH, BALL_SPEED, OFFSET_PADDLE, PADDLE_WIDTH
from utils.pong.objects.ball import Ball
from utils.pong.objects.objects_state import GameState
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score
from utils.serializers.game import PaddleSerializer, BallSerializer
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

    def _handle_paddle_direction(self, paddle: Paddle, delta_time):
        move = paddle.move
        if move == PaddleMove.UP:
            paddle.y = paddle.y - paddle.speed * delta_time
            paddle.y = self.handle_wall_collision(paddle.y)
        elif move == PaddleMove.DOWN:
            paddle.y = paddle.y + paddle.speed * delta_time
            paddle.y = self.handle_wall_collision(paddle.y)
        elif move == PaddleMove.IDLE:
            pass

    def _is_left_paddle_collision(self):
        return (self.ball.get_x() - self.ball.get_radius() <= self.paddle_pL.get_x() + self.paddle_pL.get_width() and
                self.ball.get_x() >= self.paddle_pL.get_x() and
                self.ball.get_y() >= self.paddle_pL.get_y() and
                self.ball.get_y() <= self.paddle_pL.get_y() + self.paddle_pL.get_height())
    
    
    def _is_right_paddle_collision(self):
        return (self.ball.get_x() + self.ball.get_radius() >= self.paddle_pR.get_x() and
                self.ball.get_x() <= self.paddle_pR.get_x() + self.paddle_pR.get_width() and
                self.ball.get_y() >= self.paddle_pR.get_y() and
                self.ball.get_y() <= self.paddle_pR.get_y() + self.paddle_pR.get_height())
        

    def _game_loop(self):
        current_time = time.time()
        # Hack !
        if self.last_update == -1:
            delta_time = 0
        else:
            delta_time = current_time - self.last_update

        #We use this to sync our objects with redis.
        self.ball.update()
        self.paddle_pL.update()
        self.paddle_pR.update()
        self.score_pL.update()
        self.score_pR.update()


        self.ball.dx *= 1.001
        self.ball.dy *= 1.001

        self.ball.x += self.ball.dx * delta_time
        self.ball.y += self.ball.gy * delta_time

        self._handle_paddle_direction(self.paddle_pL, delta_time)
        self._handle_paddle_direction(self.paddle_pR, delta_time)

        # Ball collision with top and bottom walls
        if self.ball.get_y() <= self.ball.get_radius() or self.ball.get_y() >= CANVAS_HEIGHT - self.ball.get_radius():
            if self.ball.get_y() < self.ball.get_radius():
                self.ball.set_y(self.ball.get_radius())  # Correct ball position
            elif self.ball.get_y() > CANVAS_HEIGHT - self.ball.get_radius():
                self.ball.set_y(CANVAS_HEIGHT - self.ball.get_radius())  # Correct ball position
            # Reverse ball's vertical direction
            self.ball.set_dy(self.ball.get_dy() * -1)

        # Left paddle collision
        if(self._is_left_paddle_collision()):
            relative_hit_pos = (self.ball.get_y() - self.paddle_pL.get_y()) / self.paddle_pL.get_height() - 0.5
            angle_factor = 2.0
            new_dy = relative_hit_pos * angle_factor * BALL_SPEED
            self.ball.set_dx(abs(self.ball.get_dx()))  # Ensure ball moves right
            self.ball.set_dy(new_dy)
            self.ball.set_x(self.paddle_pL.get_x() + self.paddle_pL.get_width() + self.ball.get_radius())

        # Right paddle collision
        if(self._is_right_paddle_collision()):
            relative_hit_pos = (self.ball.get_y() - self.paddle_pR.get_y()) / self.paddle_pR.get_height() - 0.5
            angle_factor = 2.0
            new_dy = relative_hit_pos * angle_factor * BALL_SPEED
            self.ball.set_dx(-abs(self.ball.get_dx()))  # Ensure ball moves left
            self.ball.set_dy(new_dy)
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

    def set_result(self, disconnect=False):
        winner = Player()
        loser = Player()

        if disconnect is True:
            if self.redis.hget(name="consumers_channels", key=str(self.game.pL.id)) is None:
                self.score_pL.set_score(0)
                self.score_pR.set_score(self.game.points_to_win)
            if self.redis.hget(name="consumers_channels", key=str(self.game.pR.id)) is None:
                self.score_pR.set_score(0)
                self.score_pL.set_score(self.game.points_to_win)

        if self.score_pL.get_score() > self.score_pR.get_score():
            winner.client = Clients.get_client_by_id(self.game.pL.client_id)
            winner.score = self.score_pL.get_score()
            loser.client = Clients.get_client_by_id(self.game.pR.client_id)
            loser.score = self.score_pR.get_score()
        elif self.score_pL.get_score() < self.score_pR.get_score():
            winner.client = Clients.get_client_by_id(self.game.pR.client_id)
            winner.score = self.score_pR.get_score()
            loser.client = Clients.get_client_by_id(self.game.pL.client_id)
            loser.score = self.score_pL.get_score()

        loser.save()
        winner.save()
        finished_game = Game.objects.create(id=self.game.game_id, winner=winner, loser=loser,
                                            points_to_win=self.game.points_to_win)
        self.save_player_info(loser, finished_game)
        self.save_player_info(winner, finished_game)

    def save_player_info(self, player, finished_game):
        player.game = finished_game
        player.client.stats.games.add(finished_game)
        player.client.stats.save()
        player.save()
