from dataclasses import dataclass

from redis.asyncio import Redis
from redis.commands.json.path import Path

from utils.pong.enums import PaddleMove
from utils.pong.objects import PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, CANVAS_HEIGHT


@dataclass
class Paddle:
    def __init__(self, redis=None, game_id=None, player_id=None):
        self._redis: Redis = redis
        self.width: float = PADDLE_WIDTH
        self.height: float = PADDLE_HEIGHT
        self.x: float = 0
        self.y: float = (CANVAS_HEIGHT / 2) - (PADDLE_HEIGHT / 2)
        self.speed: float = PADDLE_SPEED
        self.move: PaddleMove = PaddleMove.IDLE
        self.game_key = f'game:{game_id}'
        self.player_id = player_id

    async def update(self):
        # print(self)
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

    async def get_move(self):
        return await self._redis.json().get(self.game_key, Path('players[?(@.id=="{}")].paddle.move'.format(self.player_id)))

    # ── Setter ────────────────────────────────────────────────────────────────────────

    async def set_width(self, width):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.width'.format(self.player_id)), width)
        self.width = width

    async def set_height(self, height):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.height'.format(self.player_id)), height)
        self.height = height

    async def set_x(self, x):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.x'.format(self.player_id)), x)
        self.x = x

    async def set_y(self, y):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.y'.format(self.player_id)), y)
        self.y = y

    async def set_speed(self, speed):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.speed'.format(self.player_id)), speed)
        self.speed = speed

    async def set_move(self, move):
        await self._redis.json().set(self.game_key, Path('players[?(@.id=="{}")].paddle.move'.format(self.player_id)), move)
        self.move = move

    # ── Helper Methods for Incrementing/Decrementing ─────────────────────────────────

    async def increase_x(self):
        current_x = await self.get_x()
        await self.set_x(current_x + await self.get_speed())

    async def decrease_x(self):
        current_x = await self.get_x()
        await self.set_x(current_x - await self.get_speed())

    #
    async def handle_wall_collision(self, y) -> float:
        height = await self.get_height()
        if y <= 0:
            return 0    
        elif y + height >= CANVAS_HEIGHT:
            return CANVAS_HEIGHT - height
        else:
            return y

    #I changed both function below so it doesnt even move the paddle if its gonna be out of bound
    async def increase_y(self, delta_time):
        current_y = await self.get_y() + (await self.get_speed() * delta_time)
        current_y = await self.handle_wall_collision(current_y)
        await self.set_y(current_y)

    async def decrease_y(self, delta_time):
        current_y = await self.get_y() - (await self.get_speed() * delta_time)
        current_y = await self.handle_wall_collision(current_y)
        await self.set_y(current_y)

    async def increase_speed(self):
        current_speed = await self.get_speed()
        await self.set_speed(current_speed + 0) #Later 

    async def decrease_speed(self):
        current_speed = await self.get_speed()
        await self.set_speed(current_speed - 0) #later

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