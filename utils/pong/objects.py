from dataclasses import dataclass

from utils.pong.enums import Side

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
    radius: float = BALL_RADIUS
    x: float = CANVAS_WIDTH / 2
    y: float = CANVAS_HEIGHT / 2
    dx: float = BALL_SPEED
    dy: float = BALL_SPEED

@dataclass
class Paddle:
    width:float = PADDLE_WIDTH
    height:float = PADDLE_HEIGHT
    x:float = 0
    y:float = 0
    speed:float = PADDLE_SPEED