from utils.pong.objects.ball import Ball
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score


class GameState:
    """Class to store the current state of the game"""

    def __init__(self, ball, paddle_p1, paddle_p2, score_p1, score_p2):
        self.ball = ball
        self.paddle_p1 = paddle_p1
        self.paddle_p2 = paddle_p2
        self.score_p1 = score_p1
        self.score_p2 = score_p2

    @classmethod
    def create_copy(cls, game):
        ball_copy = Ball()
        ball_copy.radius = game.ball.radius
        ball_copy.x = game.ball.x
        ball_copy.y = game.ball.y
        ball_copy.dx = game.ball.dx
        ball_copy.dy = game.ball.dy

        paddle_p1_copy = Paddle()
        paddle_p1_copy.width = game.paddle_p1.width
        paddle_p1_copy.height = game.paddle_p1.height
        paddle_p1_copy.x = game.paddle_p1.x
        paddle_p1_copy.y = game.paddle_p1.y
        paddle_p1_copy.speed = game.paddle_p1.speed

        paddle_p2_copy = Paddle()
        paddle_p2_copy.width = game.paddle_p2.width
        paddle_p2_copy.height = game.paddle_p2.height
        paddle_p2_copy.x = game.paddle_p2.x
        paddle_p2_copy.y = game.paddle_p2.y
        paddle_p2_copy.speed = game.paddle_p2.speed

        score_p1_copy = Score()
        score_p1_copy.score = game.score_p1.score

        score_p2_copy = Score()
        score_p2_copy.score = game.score_p2.score

        return cls(ball_copy, paddle_p1_copy, paddle_p2_copy, score_p1_copy, score_p2_copy)

    @staticmethod
    def get_differences(current_state, previous_state):
        """
        Calculate differences between current and previous game states.

        Args:
            current_state: Current state containing ball, paddles, and scores
            previous_state: Previous state containing ball, paddles, and scores

        Returns:
            dict: Dictionary containing all differences organized by object type
        """
        differences = {
            'ball': {},
            'paddle_p1': {},
            'paddle_p2': {},
            'score_p1': {},
            'score_p2': {}
        }

        # Compare Ball properties
        if current_state.ball and previous_state.ball:
            for attr in ['x', 'y', 'dx', 'dy', 'radius']:
                curr_val = getattr(current_state.ball, attr)
                prev_val = getattr(previous_state.ball, attr)
                if curr_val != prev_val:
                    differences['ball'][attr] = True

        # Compare Paddle 1 properties
        if current_state.paddle_p1 and previous_state.paddle_p1:
            for attr in ['x', 'y', 'width', 'height', 'speed']:
                curr_val = getattr(current_state.paddle_p1, attr)
                prev_val = getattr(previous_state.paddle_p1, attr)
                if curr_val != prev_val:
                    differences['paddle_p1'][attr] = True

        # Compare Paddle 2 properties
        if current_state.paddle_p2 and previous_state.paddle_p2:
            for attr in ['x', 'y', 'width', 'height', 'speed']:
                curr_val = getattr(current_state.paddle_p2, attr)
                prev_val = getattr(previous_state.paddle_p2, attr)
                if curr_val != prev_val:
                    differences['paddle_p2'][attr] = True

        # Compare Score 1
        if current_state.score_p1 and previous_state.score_p1:
            curr_score = current_state.score_p1.score
            prev_score = previous_state.score_p1.score
            if curr_score != prev_score:
                differences['score_p1']['score'] = True

        # Compare Score 2
        if current_state.score_p2 and previous_state.score_p2:
            curr_score = current_state.score_p2.score
            prev_score = previous_state.score_p2.score
            if curr_score != prev_score:
                differences['score_p2']['score'] = True

        return differences
