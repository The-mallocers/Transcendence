import random
import re


def generate_unique_code():
    from apps.game.models import Game
    while True:
        code = random.randint(1000, 9999)
        if not Game.objects.filter(id=code).exists():
            return code

class ServiceError(Exception):
    def __init__(self, message='An error occured', code=400):
        self.message = message
        self.code = code
        super().__init__(f'{message} (Error Code: {code})')