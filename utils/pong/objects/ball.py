from dataclasses import dataclass

from redis.asyncio import Redis
from redis.commands.json.path import Path

from utils.pong.objects import BALL_RADIUS, CANVAS_WIDTH, CANVAS_HEIGHT, BALL_SPEED


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