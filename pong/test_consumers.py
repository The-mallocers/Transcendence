# disgusting claude generated pong game, obviously not great, but its a proof of concept

import json
from channels.generic.websocket import WebsocketConsumer
import time
from dataclasses import dataclass
import math
import random
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@dataclass
class GameState:
    # Canvas dimensions
    CANVAS_WIDTH = 1000
    CANVAS_HEIGHT = 500

    # Paddle dimensions
    PADDLE_WIDTH = 100
    PADDLE_HEIGHT = 10

    # Ball properties
    BALL_RADIUS = 10
    BALL_SPEED = 2

    def __init__(self):
        # Paddle positions (x coordinate of left edge)
        self.top_paddle_x = (self.CANVAS_WIDTH - self.PADDLE_WIDTH) / 2
        self.bottom_paddle_x = (self.CANVAS_WIDTH - self.PADDLE_WIDTH) / 2

        # Ball position and velocity
        self.ball_x = self.CANVAS_WIDTH / 2
        self.ball_y = self.CANVAS_HEIGHT / 2
        self.ball_dx = self.BALL_SPEED
        self.ball_dy = self.BALL_SPEED

        # Scores
        self.top_score = 0
        self.bottom_score = 0

        # Game state
        self.game_active = True

    def to_dict(self):
        return {
            'top_paddle_x': self.top_paddle_x,
            'bottom_paddle_x': self.bottom_paddle_x,
            'ball_x': self.ball_x,
            'ball_y': self.ball_y,
            'top_score': self.top_score,
            'bottom_score': self.bottom_score,
            'game_active': self.game_active
        }


class MyConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_state = GameState()
        self.paddle_speed = 20
        self.last_update = time.time()
        self.game_loop_task = None

    def connect(self):
        self.accept()
        print("Je me suis connecter wahooo")
        self.start_game_loop()
        self.send_game_state()

    def disconnect(self, close_code):
        if self.game_loop_task:
            self.game_loop_task.cancel()

    def game_loop(self):
        while True:
            self.update_game_state()
            self.send_game_state()
            time.sleep(1 / 60)  # 60 FPS

    def start_game_loop(self):
        import threading
        self.game_loop_task = threading.Thread(target=self.game_loop,
                                               daemon=True)
        self.game_loop_task.start()

    def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'paddle_move':
            self.handle_paddle_move(data)

    def handle_paddle_move(self, data):
        paddle = data.get('paddle')  # 'top' or 'bottom'
        direction = data.get('direction')  # 'left' or 'right'

        if paddle == 'top':
            if direction == 'left':
                self.game_state.top_paddle_x = max(0,
                                                   self.game_state.top_paddle_x - self.paddle_speed)
            elif direction == 'right':
                self.game_state.top_paddle_x = min(
                    self.game_state.CANVAS_WIDTH - self.game_state.PADDLE_WIDTH,
                    self.game_state.top_paddle_x + self.paddle_speed)

        elif paddle == 'bottom':
            if direction == 'left':
                self.game_state.bottom_paddle_x = max(0,
                                                      self.game_state.bottom_paddle_x - self.paddle_speed)
            elif direction == 'right':
                self.game_state.bottom_paddle_x = min(
                    self.game_state.CANVAS_WIDTH - self.game_state.PADDLE_WIDTH,
                    self.game_state.bottom_paddle_x + self.paddle_speed)

    def update_game_state(self):
        if not self.game_state.game_active:
            return

        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        # Update ball position
        self.game_state.ball_x += self.game_state.ball_dx * dt * 60
        self.game_state.ball_y += self.game_state.ball_dy * dt * 60

        # Check for collisions with walls
        if (self.game_state.ball_x <= self.game_state.BALL_RADIUS or
                self.game_state.ball_x >= self.game_state.CANVAS_WIDTH - self.game_state.BALL_RADIUS):
            self.game_state.ball_dx *= -1

        # Check for collision with paddles
        # Top paddle
        if (
                self.game_state.ball_y <= self.game_state.PADDLE_HEIGHT + self.game_state.BALL_RADIUS and
                self.game_state.top_paddle_x <= self.game_state.ball_x <=
                self.game_state.top_paddle_x + self.game_state.PADDLE_WIDTH):
            self.game_state.ball_dy = abs(self.game_state.ball_dy)

        # Bottom paddle
        if (self.game_state.ball_y >= self.game_state.CANVAS_HEIGHT -
                self.game_state.PADDLE_HEIGHT - self.game_state.BALL_RADIUS and
                self.game_state.bottom_paddle_x <= self.game_state.ball_x <=
                self.game_state.bottom_paddle_x + self.game_state.PADDLE_WIDTH):
            self.game_state.ball_dy = -abs(self.game_state.ball_dy)

        # Check for scoring
        if self.game_state.ball_y <= 0:
            self.game_state.bottom_score += 1
            self.reset_ball()
        elif self.game_state.ball_y >= self.game_state.CANVAS_HEIGHT:
            self.game_state.top_score += 1
            self.reset_ball()

    def reset_ball(self):
        self.game_state.ball_x = self.game_state.CANVAS_WIDTH / 2
        self.game_state.ball_y = self.game_state.CANVAS_HEIGHT / 2
        self.game_state.ball_dx = self.game_state.BALL_SPEED * (
            1 if random.random() > 0.5 else -1)
        self.game_state.ball_dy = self.game_state.BALL_SPEED * (
            1 if random.random() > 0.5 else -1)

    def send_game_state(self):
        # print("sending gamestate to client")
        self.send(text_data=json.dumps({
            'type': 'game_state_update',
            'state': self.game_state.to_dict()
        }))

#CHAT GPT ASYNC VERSION




















import json
from channels.generic.websocket import AsyncWebsocketConsumer
import time
from dataclasses import dataclass
import random
import asyncio


@dataclass
class GameState:
    # Canvas dimensions
    CANVAS_WIDTH = 1000
    CANVAS_HEIGHT = 500

    # Paddle dimensions
    PADDLE_WIDTH = 10
    PADDLE_HEIGHT = 100

    # Ball properties
    BALL_RADIUS = 10
    BALL_SPEED = 2

    def __init__(self):
        # Paddle positions (y coordinate of top edge)
        self.left_paddle_y = (self.CANVAS_HEIGHT - self.PADDLE_HEIGHT) / 2
        self.right_paddle_y = (self.CANVAS_HEIGHT - self.PADDLE_HEIGHT) / 2

        # Ball position and velocity
        self.ball_x = self.CANVAS_WIDTH / 2
        self.ball_y = self.CANVAS_HEIGHT / 2
        self.ball_dx = self.BALL_SPEED
        self.ball_dy = self.BALL_SPEED

        # Scores
        self.left_score = 0
        self.right_score = 0

        # Game state
        self.game_active = True

    def to_dict(self):
        return {
            'left_paddle_y': self.left_paddle_y,
            'right_paddle_y': self.right_paddle_y,
            'ball_x': self.ball_x,
            'ball_y': self.ball_y,
            'left_score': self.left_score,
            'right_score': self.right_score,
            'game_active': self.game_active
        }


class MyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_state = GameState()
        self.paddle_speed = 20
        self.last_update = time.time()
        self.game_loop_task = None

    async def connect(self):
        await self.accept()
        print("Connected to WebSocket!")
        self.game_loop_task = asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        if self.game_loop_task:
            self.game_loop_task.cancel()

    async def game_loop(self):
        try:
            while True:
                self.update_game_state()
                await self.send_game_state()
                await asyncio.sleep(1 / 60)  # 60 FPS
        except asyncio.CancelledError:
            pass

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'paddle_move':
            self.handle_paddle_move(data)

    def handle_paddle_move(self, data):
        paddle = data.get('paddle')  # 'left' or 'right'
        direction = data.get('direction')  # 'up' or 'down'

        if paddle == 'left':
            if direction == 'up':
                self.game_state.left_paddle_y = max(0,
                                                    self.game_state.left_paddle_y - self.paddle_speed)
            elif direction == 'down':
                self.game_state.left_paddle_y = min(
                    self.game_state.CANVAS_HEIGHT - self.game_state.PADDLE_HEIGHT,
                    self.game_state.left_paddle_y + self.paddle_speed)

        elif paddle == 'right':
            if direction == 'up':
                self.game_state.right_paddle_y = max(0,
                                                     self.game_state.right_paddle_y - self.paddle_speed)
            elif direction == 'down':
                self.game_state.right_paddle_y = min(
                    self.game_state.CANVAS_HEIGHT - self.game_state.PADDLE_HEIGHT,
                    self.game_state.right_paddle_y + self.paddle_speed)

    def update_game_state(self):
        if not self.game_state.game_active:
            return

        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        # Update ball position
        self.game_state.ball_x += self.game_state.ball_dx * dt * 60
        self.game_state.ball_y += self.game_state.ball_dy * dt * 60

        # Check for collisions with walls (top and bottom)
        if (self.game_state.ball_y <= self.game_state.BALL_RADIUS or
                self.game_state.ball_y >= self.game_state.CANVAS_HEIGHT - self.game_state.BALL_RADIUS):
            self.game_state.ball_dy *= -1

        # Check for collision with paddles
        # Left paddle
        if (
                self.game_state.ball_x <= self.game_state.PADDLE_WIDTH + self.game_state.BALL_RADIUS and
                self.game_state.left_paddle_y <= self.game_state.ball_y <=
                self.game_state.left_paddle_y + self.game_state.PADDLE_HEIGHT):
            self.game_state.ball_dx = abs(self.game_state.ball_dx)

        # Right paddle
        if (self.game_state.ball_x >= self.game_state.CANVAS_WIDTH -
                self.game_state.PADDLE_WIDTH - self.game_state.BALL_RADIUS and
                self.game_state.right_paddle_y <= self.game_state.ball_y <=
                self.game_state.right_paddle_y + self.game_state.PADDLE_HEIGHT):
            self.game_state.ball_dx = -abs(self.game_state.ball_dx)

        # Check for scoring
        if self.game_state.ball_x <= 0:
            self.game_state.right_score += 1
            self.reset_ball()
        elif self.game_state.ball_x >= self.game_state.CANVAS_WIDTH:
            self.game_state.left_score += 1
            self.reset_ball()

    def reset_ball(self):
        self.game_state.ball_x = self.game_state.CANVAS_WIDTH / 2
        self.game_state.ball_y = self.game_state.CANVAS_HEIGHT / 2
        self.game_state.ball_dx = self.game_state.BALL_SPEED * (
            1 if random.random() > 0.5 else -1)
        self.game_state.ball_dy = self.game_state.BALL_SPEED * (
            1 if random.random() > 0.5 else -1)

    async def send_game_state(self):
        await self.send(text_data=json.dumps({
            'type': 'game_state_update',
            'state': self.game_state.to_dict()
        }))
