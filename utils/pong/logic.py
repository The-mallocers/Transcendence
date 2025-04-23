import asyncio
import logging
import math
import random
import time

from apps.client.models import Clients
from apps.game.models import Game
from apps.player.models import Player
from utils.enums import EventType, ResponseAction
from utils.enums import GameStatus
from utils.enums import PaddleMove
from utils.pong.objects import * 
from utils.pong.objects.ball import Ball
from utils.pong.objects.objects_state import GameState
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score
from utils.serializers.game import PaddleSerializer, BallSerializer
from utils.websockets.channel_send import send_group
from django.db.models import F

class PongLogic:
    def __init__(self, game: Game, redis): 
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
            time.sleep(1 / FPS)
        except asyncio.CancelledError:
            pass
    
    def _game_loop(self):
        current_time = time.time()
        delta_time = self._compute_delta(current_time)
        self._pull_all_from_redis()
        self._handle_movement(delta_time)
        self._handle_wall_collision()
        self._handle_paddle_collision(self.paddle_pL, is_left=True)
        self._handle_paddle_collision(self.paddle_pR, is_left=False)
        self._handle_score()
        self._push_all_to_redis()
        self._handle_end_game()
        self.last_update = current_time

    def _handle_end_game(self):
        if self.score_pL.score >= self.points_to_win:
            self.game.rset_status(GameStatus.ENDING)
        elif self.score_pR.score >= self.points_to_win:
            self.game.rset_status(GameStatus.ENDING)

    def _handle_score(self):
        if self.ball.x <= 0 + PADDING_SCORE:
            self.score_pR.score += 1
            self._reset_ball(self.ball)
        elif self.ball.x >= CANVAS_WIDTH - PADDING_SCORE:
            self.score_pL.score += 1
            self._reset_ball(self.ball)

    def _compute_delta(self, current_time):
        if self.last_update == -1:
            delta_time = 0
        else:
            delta_time = current_time - self.last_update
        return delta_time

    def _handle_wall_collision(self):
        if self.ball.y <= self.ball.radius or self.ball.y >= CANVAS_HEIGHT - self.ball.radius:
            if self.ball.y < self.ball.radius:
                self.ball.y = self.ball.radius
            elif self.ball.y > CANVAS_HEIGHT - self.ball.radius:
                self.ball.y = CANVAS_HEIGHT - self.ball.radius
            self.ball.dy = self.ball.dy * -1

    def _handle_movement(self, delta_time):

        self.ball.x += self.ball.dx * delta_time
        self.ball.y += self.ball.dy * delta_time
        self._handle_paddle_direction(self.paddle_pL, delta_time)
        self._handle_paddle_direction(self.paddle_pR, delta_time)

    def _handle_paddle_collision(self, paddle, is_left):
        if self._is_paddle_collision(paddle):
            
            # Calculate how far from the paddle center the ball hit
            relative_hit_pos = (self.ball.y - paddle.y) / paddle.height - 0.5
            relative_hit_pos = max(min(relative_hit_pos, MAX_ANGLE_FACTOR), -MAX_ANGLE_FACTOR)
            
            current_speed = math.sqrt(self.ball.dx**2 + self.ball.dy**2)
    
            #We dont want too vertical of a movement
            max_vertical_component = current_speed * math.sqrt(1 - MIN_HORIZONTAL_PERCENT**2)
            
            self.ball.dy = relative_hit_pos * ANGLE_FACTOR * current_speed
            self.ball.dy = max(min(self.ball.dy, max_vertical_component), -max_vertical_component)
            
            dx_squared = current_speed**2 - self.ball.dy**2
            dx_magnitude = math.sqrt(max(dx_squared, 0.01))

            if is_left:
                self.ball.dx = dx_magnitude
                self.ball.x = paddle.x + paddle.width + self.ball.radius
            else:
                self.ball.dx = -dx_magnitude
                self.ball.x = paddle.x - self.ball.radius
            self.ball.dx = min(self.ball.dx * ACCEL, MAX_SPEED)
            self.ball.dy = min(self.ball.dy * ACCEL, MAX_SPEED)


    def _handle_paddle_direction(self, paddle: Paddle, delta_time):
        move = paddle.move
        if move == PaddleMove.UP:
            paddle.y = paddle.y - paddle.speed * delta_time
            paddle.y = paddle.handle_wall_collision(paddle.y)
        elif move == PaddleMove.DOWN:
            paddle.y = paddle.y + paddle.speed * delta_time
            paddle.y = paddle.handle_wall_collision(paddle.y)
        elif move == PaddleMove.IDLE:
            pass

    def _is_paddle_collision(self, paddle: Paddle):
        closest_x = max(paddle.x, min(self.ball.x, paddle.x + paddle.width))
        closest_y = max(paddle.y - PADDING_PADDLE, min(self.ball.y, paddle.y + paddle.height + PADDING_PADDLE))
       
        distance_x = self.ball.x - closest_x 
        distance_y = self.ball.y - closest_y 

        distance_squared = distance_x ** 2 + distance_y ** 2
        return distance_squared <= self.ball.radius ** 2

    def _reset_ball(self, ball):
        ball.x = CANVAS_WIDTH / 2
        ball.y = CANVAS_HEIGHT / 2
        
        angle_options = [
            random.uniform(math.radians(40), math.radians(60)),    # Right-up
            random.uniform(math.radians(120), math.radians(140)),  # Left-up
            random.uniform(math.radians(220), math.radians(240)),  # Left-down
            random.uniform(math.radians(300), math.radians(320))   # Right-down
        ]
        
        angle = random.choice(angle_options)
        ball.dx = BALL_SPEED * math.cos(angle)
        ball.dy = BALL_SPEED * math.sin(angle)
    
    def _push_all_to_redis(self):
        self.ball.push_to_redis()
        self.paddle_pL.push_to_redis()
        self.paddle_pR.push_to_redis()
        self.score_pL.push_to_redis()
        self.score_pR.push_to_redis()
        
    def _pull_all_from_redis(self):
        self.ball.update()
        self.paddle_pL.update()
        self.paddle_pR.update()
        self.score_pL.update()
        self.score_pR.update()
        
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

    def set_result(self, disconnect=False):
        winner = Player()
        loser = Player()
        winner.my_init()
        loser.my_init()

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
        
        #mmr gain would happen here.
        winner.client.stats.wins = F('wins') + 1
        loser.client.stats.losses = F('losses') + 1
        self.save_player_info(loser, finished_game)
        self.save_player_info(winner, finished_game)

    def save_player_info(self, player, finished_game):
        player.game = finished_game
        player.client.stats.games.add(finished_game)
        player.client.stats.total_game = F('total_game') + 1
        player.client.stats.save()
        player.save()