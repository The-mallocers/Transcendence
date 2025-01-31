import json
import time
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from dataclasses import dataclass

BALL_SPEED = 2
PADDLE_SPEED = 10
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_RADIUS = 2
FPS = 60
OFFSET_PADDLE = 25

class MyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_state = GameState()
        self.game_loop_task = None
        self.last_update:float = time.time()

    async def connect(self):
        await self.accept()
        self.game_loop_task = asyncio.create_task(self.game_loop())
        #should start game loop

    #close code is provided by django, and informs us why we disconnected.
    async def disconnect(self, close_code):
        if self.game_loop_task:
            self.game_loop_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'paddle_move':
            self.handleMove(data)
    
    async def send_game_state(self):
        await self.send(text_data=json.dumps({
            'type': 'game_state_update',
            'state': self.game_state.to_dict()
        }))

    async def game_loop(self):
        try:
            while True:
                self.update_game_state()
                await self.send_game_state()
                await asyncio.sleep(1 / FPS)
        except asyncio.CancelledError:
            pass

    def update_game_state(self):
        if not self.game_state.active:
            return
        current_time = time.time()
        delta_time = current_time - self.last_update
        ball = self.game_state.ball

        #implementing acceleration with time
        ball.dx *= 1.001
        ball.dy *= 1.001
        
        ball.x += ball.dx * delta_time * FPS
        ball.y += ball.dy * delta_time * FPS

        # Wall bounces (with akward code otherwise ball get stuck to wall sometimes)
        if ball.y <= ball.radius or ball.y >= self.game_state.CANVAS_HEIGHT - ball.radius:
            if ball.y < ball.radius:
                ball.y = ball.radius
            elif ball.y > self.game_state.CANVAS_HEIGHT - ball.radius:
                ball.y = self.game_state.CANVAS_HEIGHT - ball.radius
            ball.dy *= -1


        # Paddle collisions
        l_paddle = self.game_state.l_paddle
        r_paddle = self.game_state.r_paddle

        # Left paddle collision
        if (ball.x - ball.radius <= l_paddle.x + l_paddle.width and 
            ball.x >= l_paddle.x and 
            ball.y >= l_paddle.y and 
            ball.y <= l_paddle.y + l_paddle.height):
            ball.dx = abs(ball.dx)  # Ensure ball moves right
            ball.x = l_paddle.x + l_paddle.width + ball.radius

        # Right paddle collision
        if (ball.x + ball.radius >= r_paddle.x and 
            ball.x <= r_paddle.x + r_paddle.width and 
            ball.y >= r_paddle.y and 
            ball.y <= r_paddle.y + r_paddle.height):
            ball.dx = -abs(ball.dx)  # Ensure ball moves left
            ball.x = r_paddle.x - ball.radius

        # Scoring
        if ball.x <= 0:
            self.game_state.right_score += 1
            self.reset_ball()
        elif ball.x >= self.game_state.CANVAS_WIDTH:
            self.game_state.left_score += 1
            self.reset_ball()

        self.last_update = current_time

    def reset_ball(self):
        self.game_state.ball.x = self.game_state.CANVAS_WIDTH / 2
        self.game_state.ball.y = self.game_state.CANVAS_HEIGHT / 2
        self.game_state.ball.dx = BALL_SPEED * ( 1 if random.random() > 0.5 else -1)
        self.game_state.ball.dy = BALL_SPEED * ( 1 if random.random() > 0.5 else -1)


    def handleMove(self, data):
        paddle_data = data.get('paddle')
        direction = data.get('direction')
        paddle = None

        if paddle_data == 'left':
            paddle = self.game_state.l_paddle
        elif paddle_data == 'right':
            paddle = self.game_state.r_paddle
        if paddle:
            if direction == 'up':
                paddle.y = max(0, paddle.y - paddle.speed)
            elif direction == 'down': 
                limit = self.game_state.CANVAS_HEIGHT - paddle.height
                paddle.y = min(limit, paddle.y + paddle.speed)

# class GameState:
#     CANVAS_WIDTH: int = 1000
#     CANVAS_HEIGHT: int = 500
#
#     def __init__(self):
#         self.ball: Ball = Ball(x = self.CANVAS_WIDTH / 2, y = self.CANVAS_HEIGHT / 2)
#         self.l_paddle: Paddle = Paddle(x = OFFSET_PADDLE, y = self.CANVAS_HEIGHT / 2)
#         self.r_paddle: Paddle = Paddle(x = self.CANVAS_WIDTH - Paddle.width - OFFSET_PADDLE, y = self.CANVAS_HEIGHT / 2)
#         self.game_active:bool = True
#         self.left_score:int = 0
#         self.right_score:int = 0
#
#     def to_dict(self):
#         return {
#             'left_paddle_y': self.l_paddle.y,
#             'right_paddle_y': self.r_paddle.y,
#             'ball_x': self.ball.x,
#             'ball_y': self.ball.y,
#             'left_score': self.left_score,
#             'right_score': self.right_score,
#             'game_active': self.game_active
#         }


# @dataclass
# class Ball:
#     radius:float = BALL_RADIUS
#     x:float = 0
#     y:float = 0
#     dx:float = BALL_SPEED
#     dy:float = BALL_SPEED
#
# @dataclass
# class Paddle:
#     width:float = PADDLE_WIDTH
#     height:float = PADDLE_HEIGHT
#     x:float = 0
#     y:float = 0
#     speed:float = PADDLE_SPEED
        