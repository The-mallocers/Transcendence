from dataclasses import dataclass

from redis.commands.json.path import Path

from apps.player.models import Player
from utils.enums import PaddleMove, PlayerSide, RTables
from utils.pong.objects import PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, CANVAS_HEIGHT


@dataclass
class Paddle:
    def __init__(self, side: PlayerSide, game_id=None, redis=None, client_id=None, x=0):
        # ── Fields ────────────────────────────────────────────────────────────────────────
        self.width: float = PADDLE_WIDTH
        self.height: float = PADDLE_HEIGHT
        self.x: float = x
        self.y: float = (CANVAS_HEIGHT / 2) - (PADDLE_HEIGHT / 2)
        self.speed: float = PADDLE_SPEED
        self.side = side

        # ── Utils ─────────────────────────────────────────────────────────────────────────    
        self.redis = redis
        self.game_key = RTables.JSON_GAME(game_id)
        self.move: PaddleMove = PaddleMove.IDLE
        self.player_side = side.value

    def update(self):
        self.width = self.get_width()
        self.height = self.get_height()
        self.x = self.get_x()
        self.y = self.get_y()
        self.speed = self.get_speed()
        self.move = self.get_move()

    def push_to_redis(self):
        self.set_width(self.width)
        self.set_height(self.height)
        self.set_x(self.x)
        self.set_y(self.y)
        self.set_speed(self.speed)
        self.set_move(self.move)

    def __str__(self):
        return f'X: {self.x}, Y: {self.y}'

    # ── Getter ────────────────────────────────────────────────────────────────────────

    def get_width(self):
        return self.redis.json().get(self.game_key, Path(f'{self.player_side}.paddle.width'))

    def get_height(self):
        return self.redis.json().get(self.game_key, Path(f'{self.player_side}.paddle.height'))

    def get_x(self):
        return self.redis.json().get(self.game_key, Path(f'{self.player_side}.paddle.x'))

    def get_y(self):
        return self.redis.json().get(self.game_key, Path(f'{self.player_side}.paddle.y'))

    def get_speed(self):
        return self.redis.json().get(self.game_key, Path(f'{self.player_side}.paddle.speed'))

    def get_move(self):
        return self.redis.json().get(self.game_key, Path(f'{self.player_side}.paddle.move'))

    # ── Setter ────────────────────────────────────────────────────────────────────────

    def set_width(self, width):
        self.redis.json().set(self.game_key, Path(f'{self.player_side}.paddle.width'), width)
        self.width = width

    def set_height(self, height):
        self.redis.json().set(self.game_key, Path(f'{self.player_side}.paddle.height'), height)
        self.height = height

    def set_x(self, x):
        self.redis.json().set(self.game_key, Path(f'{self.player_side}.paddle.x'), x)
        self.x = x

    def set_y(self, y):
        self.redis.json().set(self.game_key, Path(f'{self.player_side}.paddle.y'), y)
        self.y = y

    def set_speed(self, speed):
        self.redis.json().set(self.game_key, Path(f'{self.player_side}.paddle.speed'), speed)
        self.speed = speed

    def set_move(self, move):
        self.redis.json().set(self.game_key, Path(f'{self.player_side}.paddle.move'), move)
        self.move = move

    # ── Helper Methods for Incrementing/Decrementing ─────────────────────────────────

    def increase_x(self):
        current_x = self.get_x()
        self.set_x(current_x + self.get_speed())

    def decrease_x(self):
        current_x = self.get_x()
        self.set_x(current_x - self.get_speed())

    #
    def handle_wall_collision(self, y) -> float:
        height = self.height
        if y <= 0:
            return 0
        elif y + height >= CANVAS_HEIGHT:
            return CANVAS_HEIGHT - height
        else:
            return y

    # I changed both function below so it doesnt even move the paddle if its gonna be out of bound
    def increase_y(self, delta_time):
        current_y = self.get_y() + (self.get_speed() * delta_time)
        current_y = self.handle_wall_collision(current_y)
        self.set_y(current_y)

    def decrease_y(self, delta_time):
        current_y = self.get_y() - (self.get_speed() * delta_time)
        current_y = self.handle_wall_collision(current_y)
        self.set_y(current_y)

    def increase_speed(self):
        current_speed = self.get_speed()
        self.set_speed(current_speed + 0)  # Later

    def decrease_speed(self):
        current_speed = self.get_speed()
        self.set_speed(current_speed - 0)  # later

    # ── Helper Methods for Multiplication/Division ─────────────────────────────────

    def multiply_x(self, factor: float):
        current_x = self.get_x()
        self.set_x(current_x * factor)

    def divide_x(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_x = self.get_x()
        self.set_x(current_x / factor)

    def multiply_y(self, factor: float):
        current_y = self.get_y()
        self.set_y(current_y * factor)

    def divide_y(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_y = self.get_y()
        self.set_y(current_y / factor)

    def multiply_speed(self, factor: float):
        current_speed = self.get_speed()
        self.set_speed(current_speed * factor)

    def divide_speed(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_speed = self.get_speed()
        self.set_speed(current_speed / factor)
