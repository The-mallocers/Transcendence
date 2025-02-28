import logging
from dataclasses import dataclass

from redis.asyncio import Redis
from redis.commands.json.path import Path

BALL_SPEED = 2
PADDLE_SPEED = 10
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_RADIUS = 1
FPS = 60
OFFSET_PADDLE = 25
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 500

@dataclass
class Ball:
    def __init__(self, redis=None, game_id=None):
        self.radius: float = BALL_RADIUS
        self.x: float = CANVAS_WIDTH / 2
        self.y: float = CANVAS_HEIGHT / 2
        self.dx: float = BALL_SPEED
        self.dy: float = BALL_SPEED
        self._redis: Redis = redis
        self.game_key = f'game:{game_id}'

    async def update(self):
        self.radius = await self.get_radius()
        self.x = await self.get_x()
        self.y = await self.get_y()
        self.dx = await self.get_dx()
        self.dy = await self.get_dy()

    # ── Getter ────────────────────────────────────────────────────────────────────────

    async def get_radius(self):
        return await self._redis.json().get(self.game_key, Path('ball.radius'))

    async def get_x(self):
        return await self._redis.json().get(self.game_key, Path('ball.x'))

    async def get_y(self):
        return await self._redis.json().get(self.game_key, Path('ball.y'))

    async def get_dx(self):
        return await self._redis.json().get(self.game_key, Path('ball.dx'))

    async def get_dy(self):
        return await self._redis.json().get(self.game_key, Path('ball.dy'))

    # ── Setter ────────────────────────────────────────────────────────────────────────

    async def set_radius(self, radius):
        await self._redis.json().set(self.game_key, Path('ball.radius'), radius)

    async def set_x(self, x):
        await self._redis.json().set(self.game_key, Path('ball.x'), x)

    async def set_y(self, y):
        await self._redis.json().set(self.game_key, Path('ball.y'), y)

    async def set_dx(self, dx):
        await self._redis.json().set(self.game_key, Path('ball.dx'), dx)

    async def set_dy(self, dy):
        await self._redis.json().set(self.game_key, Path('ball.dy'), dy)

    # ── Helper Methods for Incrementing/Decrementing ─────────────────────────────────

    async def increase_x(self, delta: float = 1):
        current_x = await self.get_x()
        await self.set_x(current_x + delta)

    async def decrease_x(self, delta: float = 1):
        current_x = await self.get_x()
        await self.set_x(current_x - delta)

    async def increase_y(self, delta: float = 1):
        current_y = await self.get_y()
        await self.set_y(current_y + delta)

    async def decrease_y(self, delta: float = 1):
        current_y = await self.get_y()
        await self.set_y(current_y - delta)

    async def increase_dx(self, delta: float = 1):
        current_dx = await self.get_dx()
        await self.set_dx(current_dx + delta)

    async def decrease_dx(self, delta: float = 1):
        current_dx = await self.get_dx()
        await self.set_dx(current_dx - delta)

    async def increase_dy(self, delta: float = 1):
        current_dy = await self.get_dy()
        await self.set_dy(current_dy + delta)

    async def decrease_dy(self, delta: float = 1):
        current_dy = await self.get_dy()
        await self.set_dy(current_dy - delta)

    # ── Helper Methods for Multiplication/Division ─────────────────────────────────

    async def multiply_x(self, factor: float):
        current_x = await self.get_x()
        await self.set_x(current_x * factor)

    async def divide_x(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_x = await self.get_x()
        await self.set_x(current_x / factor)

    async def multiply_y(self, factor: float):
        current_y = await self.get_y()
        await self.set_y(current_y * factor)

    async def divide_y(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_y = await self.get_y()
        await self.set_y(current_y / factor)

    async def multiply_dx(self, factor: float):
        current_dx = await self.get_dx()
        await self.set_dx(current_dx * factor)

    async def divide_dx(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_dx = await self.get_dx()
        await self.set_dx(current_dx / factor)

    async def multiply_dy(self, factor: float):
        current_dy = await self.get_dy()
        await self.set_dy(current_dy * factor)

    async def divide_dy(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_dy = await self.get_dy()
        await self.set_dy(current_dy / factor)


@dataclass
class Paddle:
    def __init__(self, redis=None, game_id=None, player_id=None):
        self.width: float = PADDLE_WIDTH
        self.height: float = PADDLE_HEIGHT
        self.x: float = 0
        self.y: float = 0
        self.speed: float = PADDLE_SPEED
        self._redis: Redis = redis
        self.game_key = f'game:{game_id}'
        self.player_id = player_id

    async def update(self):
        self.width = await self.get_width()
        self.height = await self.get_height()
        self.x = await self.get_x()
        self.y = await self.get_y()
        self.speed = await self.get_speed()

    def __str__(self):
        return f'X: {self.x}, Y: {self.y}'

    # ── Getter ────────────────────────────────────────────────────────────────────────

    async def get_width(self):
        return await self._redis.json().get(self.game_key, Path('players[?(@.id=="{}")].paddle.width'.format(self.player_id)))

    async def get_height(self):
        return await self._redis.json().get(self.game_key, Path('players[?(@.id=="{}")].paddle.height'.format(self.player_id)))

    async def get_x(self):
        return await self._redis.json().get(self.game_key, Path('players[?(@.id=="{}")].paddle.x'.format(self.player_id)))

    async def get_y(self):
        return await self._redis.json().get(self.game_key, Path('players[?(@.id=="{}")].paddle.y'.format(self.player_id)))

    async def get_speed(self):
        return await self._redis.json().get(self.game_key, Path('players[?(@.id=="{}")].paddle.speed'.format(self.player_id)))

    # ── Setter ────────────────────────────────────────────────────────────────────────

    async def set_width(self, width):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.width'.format(self.player_id)), width)

    async def set_height(self, height):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.height'.format(self.player_id)), height)

    async def set_x(self, x):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.x'.format(self.player_id)), x)

    async def set_y(self, y):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.y'.format(self.player_id)), y)

    async def set_speed(self, speed):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.speed'.format(self.player_id)), speed)

    # ── Helper Methods for Incrementing/Decrementing ─────────────────────────────────

    async def increase_x(self, delta: float = 1):
        current_x = await self.get_x()
        await self.set_x(current_x + delta)

    async def decrease_x(self, delta: float = 1):
        current_x = await self.get_x()
        await self.set_x(current_x - delta)

    async def increase_y(self, delta: float = 1):
        current_y = await self.get_y()
        await self.set_y(current_y + delta)

    async def decrease_y(self, delta: float = 1):
        current_y = await self.get_y()
        await self.set_y(current_y - delta)

    async def increase_speed(self, delta: float = 1):
        current_speed = await self.get_speed()
        await self.set_speed(current_speed + delta)

    async def decrease_speed(self, delta: float = 1):
        current_speed = await self.get_speed()
        await self.set_speed(current_speed - delta)

    # ── Helper Methods for Multiplication/Division ─────────────────────────────────

    async def multiply_x(self, factor: float):
        current_x = await self.get_x()
        await self.set_x(current_x * factor)

    async def divide_x(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_x = await self.get_x()
        await self.set_x(current_x / factor)

    async def multiply_y(self, factor: float):
        current_y = await self.get_y()
        await self.set_y(current_y * factor)

    async def divide_y(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_y = await self.get_y()
        await self.set_y(current_y / factor)

    async def multiply_speed(self, factor: float):
        current_speed = await self.get_speed()
        await self.set_speed(current_speed * factor)

    async def divide_speed(self, factor: float):
        if factor == 0:
            raise ValueError("Cannot divide by zero")
        current_speed = await self.get_speed()
        await self.set_speed(current_speed / factor)

@dataclass
class Score:
    def __init__(self, redis=None, game_id=None, player_id=None):
        self.score = 0
        self._redis: Redis = redis
        self.game_key = f'game:{game_id}'
        self.player_id = player_id

    async def get_score(self):
        await self._redis.json().get(self.game_key, Path(f'players[?(@.id=="{self.player_id}")].score'))

    async def add_score(self):
        current = await self.get_score()
        # await self._redis.json().set(self.game_key, Path(f'players[?(@.id=="{self.player_id}")].score'), current + 1)

    async def del_score(self):
        current = await self.get_score()
        # await self._redis.json().set(self.game_key, Path(f'players[?(@.id=="{self.player_id}")].score'), current - 1)
