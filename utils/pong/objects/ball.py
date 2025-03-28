from dataclasses import dataclass

from redis.commands.json.path import Path

from utils.pong.objects import BALL_RADIUS, CANVAS_WIDTH, CANVAS_HEIGHT, BALL_SPEED


@dataclass
class Ball:
    def __init__(self, game_id=None, redis=None):
        # ── Fields ────────────────────────────────────────────────────────────────────────
        self.radius: float = BALL_RADIUS
        self.x: float = CANVAS_WIDTH / 2
        self.y: float = CANVAS_HEIGHT / 2
        self.dx: float = BALL_SPEED
        self.dy: float = BALL_SPEED

        # ── Utils ─────────────────────────────────────────────────────────────────────────    
        self.redis = redis
        self.game_key = f'game:{game_id}'

    def update(self):
        self.radius = self.get_radius()
        self.x = self.get_x()
        self.y = self.get_y()
        self.dx = self.get_dx()
        self.dy = self.get_dy()

    # ── Getter ────────────────────────────────────────────────────────────────────────

    def get_radius(self):
        return self.redis.json().get(self.game_key, Path('ball.radius'))

    def get_x(self):
        return self.redis.json().get(self.game_key, Path('ball.x'))

    def get_y(self):
        return self.redis.json().get(self.game_key, Path('ball.y'))

    def get_dx(self):
        return self.redis.json().get(self.game_key, Path('ball.dx'))

    def get_dy(self):
        return self.redis.json().get(self.game_key, Path('ball.dy'))

    # ── Setter ────────────────────────────────────────────────────────────────────────

    def set_radius(self, radius):
        self.redis.json().set(self.game_key, Path('ball.radius'), radius)

    def set_x(self, x):
        self.redis.json().set(self.game_key, Path('ball.x'), x)

    def set_y(self, y):
        self.redis.json().set(self.game_key, Path('ball.y'), y)

    def set_dx(self, dx):
        self.redis.json().set(self.game_key, Path('ball.dx'), dx)

    def set_dy(self, dy):
        self.redis.json().set(self.game_key, Path('ball.dy'), dy)

    # ── Helper Methods for Incrementing/Decrementing ─────────────────────────────────

    def increase_x(self, delta: float = 1):
        current_x = self.get_x()
        self.set_x(current_x + delta)

    def decrease_x(self, delta: float = 1):
        current_x = self.get_x()
        self.set_x(current_x - delta)

    def increase_y(self, delta: float = 1):
        current_y = self.get_y()
        self.set_y(current_y + delta)

    def decrease_y(self, delta: float = 1):
        current_y = self.get_y()
        self.set_y(current_y - delta)

    def increase_dx(self, delta: float = 1):
        current_dx = self.get_dx()
        self.set_dx(current_dx + delta)

    def decrease_dx(self, delta: float = 1):
        current_dx = self.get_dx()
        self.set_dx(current_dx - delta)

    def increase_dy(self, delta: float = 1):
        current_dy = self.get_dy()
        self.set_dy(current_dy + delta)

    def decrease_dy(self, delta: float = 1):
        current_dy = self.get_dy()
        self.set_dy(current_dy - delta)

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

    def multiply_dx(self, factor: float):
        current_dx = self.get_dx()
        self.set_dx(current_dx * factor)

    def divide_dx(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_dx = self.get_dx()
        self.set_dx(current_dx / factor)

    def multiply_dy(self, factor: float):
        current_dy = self.get_dy()
        self.set_dy(current_dy * factor)

    def divide_dy(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_dy = self.get_dy()
        self.set_dy(current_dy / factor)
