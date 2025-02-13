import random
import re


def generate_unique_code():
    from apps.game.models import Game
    while True:
        code = random.randint(1000, 9999)
        if not Game.objects.filter(id=code).exists():
            return code