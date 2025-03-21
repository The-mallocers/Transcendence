import random

from django.core.exceptions import ValidationError


def create_game_id():
    from apps.game.models import Game
    while True:
        code = random.randint(0000, 9999)
        if not Game.objects.filter(id=code).exists():
            return code


def create_tournament_id():
    from apps.tournaments.models import Tournaments
    while True:
        code = random.randint(0000, 9999)
        if not Tournaments.objects.filter(id=code).exists():
            return code


def validate_even(value):
    if value % 2 != 0:
        raise ValidationError(f"%{value} is is not an even number")
