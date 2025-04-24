from utils.pong.objects.ball import Ball
from utils.pong.objects.paddle import Paddle
from utils.pong.objects.score import Score


class GameState:
    """Class to store the current state of the game"""

    def __init__(self, ball, paddle_pL, paddle_pR, score_pL, score_pR):
        self.ball = ball
        self.paddle_pL = paddle_pL
        self.paddle_pR = paddle_pR
        self.score_pL = score_pL
        self.score_pR = score_pR

    @classmethod
    def create_copy(cls, logic):
        ball_copy = Ball()
        ball_copy.radius = logic.ball.radius
        ball_copy.x = logic.ball.x
        ball_copy.y = logic.ball.y
        ball_copy.dx = logic.ball.dx
        ball_copy.dy = logic.ball.dy

        paddle_pL_copy = Paddle()
        paddle_pL_copy.width = logic.paddle_pL.width
        paddle_pL_copy.height = logic.paddle_pL.height
        paddle_pL_copy.x = logic.paddle_pL.x
        paddle_pL_copy.y = logic.paddle_pL.y
        paddle_pL_copy.speed = logic.paddle_pL.speed

        paddle_pR_copy = Paddle()
        paddle_pR_copy.width = logic.paddle_pR.width
        paddle_pR_copy.height = logic.paddle_pR.height
        paddle_pR_copy.x = logic.paddle_pR.x
        paddle_pR_copy.y = logic.paddle_pR.y
        paddle_pR_copy.speed = logic.paddle_pR.speed

        score_pL_copy = Score()
        score_pL_copy.score = logic.score_pL.score

        score_pR_copy = Score()
        score_pR_copy.score = logic.score_pR.score

        return cls(ball_copy, paddle_pL_copy, paddle_pR_copy, score_pL_copy, score_pR_copy)

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
            'paddle_pL': {},
            'paddle_pR': {},
            'score_pL': {},
            'score_pR': {},
        }

        # Compare Ball properties
        if current_state.ball and previous_state.ball:
            for attr in ['x', 'y', 'dx', 'dy', 'radius']:
                curr_val = getattr(current_state.ball, attr)
                prev_val = getattr(previous_state.ball, attr)
                if curr_val != prev_val:
                    differences['ball'][attr] = {
                        'previous': prev_val,
                        'current': curr_val,
                        'diff': curr_val - prev_val
                    }

        # Compare Paddle 1 properties
        if current_state.paddle_pL and previous_state.paddle_pL:
            for attr in ['x', 'y', 'width', 'height', 'speed']:
                curr_val = getattr(current_state.paddle_pL, attr)
                prev_val = getattr(previous_state.paddle_pL, attr)
                if curr_val != prev_val:
                    differences['paddle_pL'][attr] = {
                        'previous': prev_val,
                        'current': curr_val,
                        'diff': curr_val - prev_val
                    }

        # Compare Paddle 2 properties
        if current_state.paddle_pR and previous_state.paddle_pR:
            for attr in ['x', 'y', 'width', 'height', 'speed']:
                curr_val = getattr(current_state.paddle_pR, attr)
                prev_val = getattr(previous_state.paddle_pR, attr)
                if curr_val != prev_val:
                    differences['paddle_pR'][attr] = {
                        'previous': prev_val,
                        'current': curr_val,
                        'diff': curr_val - prev_val
                    }

        # Compare Score 1
        if current_state.score_pL and previous_state.score_pL:
            curr_score = current_state.score_pL.score
            prev_score = previous_state.score_pL.score
            if curr_score != prev_score:
                differences['score_pL']['score'] = {
                    'previous': prev_score,
                    'current': curr_score,
                    'diff': curr_score - prev_score
                }

        # Compare Score 2
        if current_state.score_pR and previous_state.score_pR:
            curr_score = current_state.score_pR.score
            prev_score = previous_state.score_pR.score
            if curr_score != prev_score:
                differences['score_pR']['score'] = {
                    'previous': prev_score,
                    'current': curr_score,
                    'diff': curr_score - prev_score
                }

        return differences
