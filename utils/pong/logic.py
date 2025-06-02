import asyncio
import logging
import math
import random
import time

from django.db.models import F
from redis.commands.json.path import Path

from apps.client.models import Clients
from apps.game.models import Game
from apps.player.models import Player
from apps.tournaments.models import Tournaments
from utils.enums import EventType, PlayerSide, ResponseAction, RTables
from utils.enums import GameStatus
from utils.enums import PaddleMove
from utils.pong.objects import *
from utils.pong.objects.ball import Ball
from utils.pong.objects.objects_state import GameState
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score
from utils.serializers.game import PaddleSerializer, BallSerializer
from utils.serializers.player import PlayerScoreSerializer
from utils.websockets.channel_send import send_group


class PongLogic:
    def __init__(self, game: Game, redis):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.redis = redis
        self.game = game
        self.game_id = game.code
        self.last_update: float = -1  # This hack is sponsored by tfreydie and prevents the random +1 score at the start

        # ── Objects ───────────────────────────────────────────────────────────────────
        self.ball: Ball = Ball(game_id=self.game_id, redis=redis)
        self.paddle_pL: Paddle = Paddle(side=PlayerSide.LEFT ,game_id=self.game_id, redis=redis, client_id=self.game.pL.client.id, x=OFFSET_PADDLE)
        self.paddle_pR: Paddle = Paddle(side=PlayerSide.RIGHT, game_id=self.game_id, redis=redis, client_id=self.game.pR.client.id, x=CANVAS_WIDTH - OFFSET_PADDLE -PADDLE_WIDTH)
        self.score_pL: Score = Score(side=PlayerSide.LEFT ,game_id=self.game_id, redis=redis, client_id=self.game.pL.client.id)
        self.score_pR: Score = Score(side=PlayerSide.RIGHT ,game_id=self.game_id, redis=redis, client_id=self.game.pR.client.id)
        self.points_to_win = self.game.points_to_win

    def game_task(self):
        try:
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

            current_speed = math.sqrt(self.ball.dx ** 2 + self.ball.dy ** 2)

            # We dont want too vertical of a movement
            max_vertical_component = current_speed * math.sqrt(1 - MIN_HORIZONTAL_PERCENT ** 2)

            self.ball.dy = relative_hit_pos * ANGLE_FACTOR * current_speed
            self.ball.dy = max(min(self.ball.dy, max_vertical_component), -max_vertical_component)

            dx_squared = current_speed ** 2 - self.ball.dy ** 2
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
            random.uniform(math.radians(40), math.radians(60)),  # Right-up
            random.uniform(math.radians(120), math.radians(140)),  # Left-up
            random.uniform(math.radians(220), math.radians(240)),  # Left-down
            random.uniform(math.radians(300), math.radians(320))  # Right-down
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
            send_group(RTables.GROUP_GAME(self.game_id), EventType.UPDATE, ResponseAction.BALL_UPDATE, BallSerializer(self.ball).data)

        if changes['paddle_pL']:
            send_group(RTables.GROUP_GAME(self.game_id), EventType.UPDATE, ResponseAction.PADDLE_LEFT_UPDATE,
                       PaddleSerializer(self.paddle_pL).data)

        if changes['paddle_pR']:
            send_group(RTables.GROUP_GAME(self.game_id), EventType.UPDATE, ResponseAction.PADDLE_RIGHT_UPDATE,
                       PaddleSerializer(self.paddle_pR).data)

        if changes['score_pL']:
            send_group(RTables.GROUP_GAME(self.game_id), EventType.UPDATE, ResponseAction.SCORE_LEFT_UPDATE,
                       self.score_pL.get_score())

        if changes['score_pR']:
            send_group(RTables.GROUP_GAME(self.game_id), EventType.UPDATE, ResponseAction.SCORE_RIGHT_UPDATE,
                       self.score_pR.get_score())

    def set_result(self, disconnect=False):
        if self.game.local == True:
            return
        winner = Player.create_player()
        loser = Player.create_player()

        if disconnect is True:
            if self.redis.hget(name=RTables.HASH_CLIENT(self.game.pL.client.id), key=str(EventType.GAME.value)) is None:
                self.score_pL.set_score(0)
                self.score_pR.set_score(self.game.points_to_win)
            if self.redis.hget(name=RTables.HASH_CLIENT(self.game.pR.client.id), key=str(EventType.GAME.value)) is None:
                self.score_pR.set_score(0)
                self.score_pL.set_score(self.game.points_to_win)
        if self.score_pL.get_score() > self.score_pR.get_score():
            winner.client = Clients.get_client_by_id(self.game.pL.client.id)
            winner.score = self.score_pL.get_score()
            loser.client = Clients.get_client_by_id(self.game.pR.client.id)
            loser.score = self.score_pR.get_score()
        elif self.score_pL.get_score() < self.score_pR.get_score():
            winner.client = Clients.get_client_by_id(self.game.pR.client.id)
            winner.score = self.score_pR.get_score()
            loser.client = Clients.get_client_by_id(self.game.pL.client.id)
            loser.score = self.score_pL.get_score()

        loser.save()
        winner.save()
        tournament = None
        if self.game.tournament:
            tournament = Tournaments.get_tournament_by_code(self.game.tournament.code)
            current_round = self.redis.json().get(RTables.JSON_TOURNAMENT(tournament.code), Path('scoreboards.current_round'))
            max_round = self.redis.json().get(RTables.JSON_TOURNAMENT(tournament.code), Path('scoreboards.num_rounds'))
            #Yes, we do not use this variable, but if you get rid of it sometimes when leaving tournament it crashes.
            client_pos = PlayerScoreSerializer(loser, context={
                'position': (max_round-current_round)*2,
                'client_id': str(loser.client.id),
                'username': loser.client.profile.username,
                'matches_played': 0,
                'matches_won': 0,
                'points': 0,
            })
            # tournament.scoreboards['scoreboards'].append(client_pos.data)
            tournament.save()
        finished_game = Game.objects.create(code=self.game.code, winner=winner, loser=loser,
                                            points_to_win=self.game.points_to_win, is_duel=self.game.rget_is_duel(), tournament=tournament)


        self.compute_mmr_change(winner, loser)
        winner.client.stats.wins = F('wins') + 1
        loser.client.stats.losses = F('losses') + 1
        self.save_player_info(loser, finished_game)
        self.game.loser = loser
        self.save_player_info(winner, finished_game)
        self.game.winner = winner

    def save_player_info(self, player, finished_game):
        player.game = finished_game
        player.save()
        player.client.stats.games.add(finished_game)
        player.client.stats.total_game = F('total_game') + 1
        player.client.stats.save()
        player.save()

    def compute_mmr_change(self, winner, loser):
            K = 50

            print(winner, loser)
            winner_mmr = winner.client.stats.mmr
            loser_mmr = loser.client.stats.mmr

            expected_win = 1 / (1 + 10 ** ((loser_mmr - winner_mmr) / 120))
            expected_loss = 1 / (1 + 10 ** ((winner_mmr - loser_mmr) / 120))

            mmr_gain = round(K * (1 - expected_win))
            mmr_loss = round(K * (0 - expected_loss))
            if (loser_mmr + mmr_loss < 0):
                mmr_loss = loser_mmr
                loser.client.stats.mmr = 0
                loser.mmr_change = -mmr_loss
            else:
                loser.client.stats.mmr = F('mmr') + mmr_loss
                loser.mmr_change = mmr_loss

            winner.mmr_change = mmr_gain
            winner.client.stats.mmr = F('mmr') + mmr_gain
