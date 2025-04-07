import random
import uuid

from django.core.exceptions import ValidationError


def create_game_id():
    from apps.game.models import Game
    while True:
        code = f"{random.randint(0, 9999):04d}"  # Génère un nombre et le formate sur 4 chiffres
        if not Game.objects.filter(id=code).exists():
            return code


def create_tournament_id():
    from apps.tournaments.models import Tournaments
    while True:
        code = random.randint(0000, 9999)
        if not Tournaments.objects.filter(id=code).exists():
            return code


def create_jti_id():
    while True:
        id = uuid.uuid4()
        from apps.auth.models import InvalidatedToken
        if not InvalidatedToken.objects.filter(jti=id).exists():
            return id


def validate_even(value):
    if value % 2 != 0:
        raise ValidationError(f"%{value} is is not an even number")


def format_validation_errors(errors):
    result = []

    def process_errors(prefix, error_dict):
        if isinstance(error_dict, dict):
            for key, value in error_dict.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                process_errors(new_prefix, value)
        elif isinstance(error_dict, list):
            error_messages = [str(error) for error in error_dict]
            result.append(f"{prefix}: {' '.join(error_messages)}")
        else:
            result.append(f"{prefix}: {error_dict}")

    process_errors("", errors)
    return "; ".join(result)
