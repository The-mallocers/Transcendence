import json
import time
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from dataclasses import dataclass

BALL_SPEED = 2
PADDLE_SPEED = 20
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_RADIUS = 2

class MyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #more game related stuff, but the above innit the superclass.
        self.game_state = GameState()

    async def connect(self):
        await self.accept()
        print("Connected succesfully")
        self.game_loop_task = asyncio.create_task(self.game_loop())
        #should start game loop

    #close code is provided by django, and informs us why we disconnected.
    async def disconnect(self, close_code):
        print("Disconnecting succesfully")
        if self.game_loop_task:
            self.game_loop_task.cancel()
        #should disconnect the client and whatever game object i have going on

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'paddle_move':
            self.handleMove(self, data)
    
    async def send_game_state(self):
        await self.send(text_data=json.dumps({
            'type': 'game_state_update',
            'state': self.game_state.to_dict()
        }))

    async def game_loop(self):
        try:
            #later this will be while a bool of some sort id assume.
            while True:
                self.update_game_state()
                await self.send_game_state()
                await asyncio.sleep(1 / 60)  # crude 60 fps, to improve with delta time later.
        except asyncio.CancelledError:
            pass

    def update_game_state(self):
        if not self.game_state.game_active:
            return


    def handleMove(self, data):
        paddle_data = data.get('paddle')
        direction = data.get('direction')
        paddle = None

        if paddle_data == 'left':
            paddle = self.game_state.l_paddle
        elif paddle_data == 'right':
            paddle = self.game_state.r_paddle
        
        if paddle:
            if direction == 'top':
                paddle.y = max(0, paddle.y - speed)
            elif direction == 'down': 
                limit = self.game_state.CANVAS_HEIGHT - paddle.heigth
                paddle.y = min(limit, paddle.y + speed)

class GameState:
    CANVAS_WIDTH: int = 1000
    CANVAS_HEIGHT: int = 500

    def __init__(self):
        self.ball: Ball = Ball()
        self.l_paddle: Paddle = Paddle(x = self.CANVAS_WIDTH * 0.2, y = self.CANVAS_HEIGHT / 2)
        self.r_paddle: Paddle = Paddle(x = self.CANVAS_WIDTH * 0.8, y = self.CANVAS_HEIGHT / 2)
        self.game_active:bool = True
        self.left_score:int = 0
        self.right_score:int = 0


    def updateGameState(self, update):
        pass
    
    def to_dict(self):
        return {
            'left_paddle_y': self.l_paddle.y,
            'right_paddle_y': self.r_paddle.y,
            'ball_x': self.ball.x,
            'ball_y': self.ball.y,
            'left_score': self.left_score,
            'right_score': self.right_score,
            'game_active': self.game_active
        }


@dataclass
class Ball:
    radius:float = BALL_RADIUS 
    x:float = 0
    y:float = 0
    dx:float = BALL_SPEED
    dy:float = BALL_SPEED
    
@dataclass
class Paddle:
    width:float = PADDLE_WIDTH
    heigth:float = PADDLE_HEIGHT
    x:float = 0
    y:float = 0
    speed:float = PADDLE_SPEED
        