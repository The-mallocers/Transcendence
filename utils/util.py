import random
import string
import uuid

from django.core.exceptions import ValidationError


def create_game_id():
    from apps.game.models import Game
    from utils.enums import RTables
    from utils.redis import RedisConnectionPool
    redis = RedisConnectionPool.get_sync_connection('GameID')
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not Game.objects.filter(code=code).exists() and not redis.exists(RTables.JSON_GAME(code)):
            return code


def create_tournament_id():
    from apps.tournaments.models import Tournaments
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))  # Génère un code aléatoire de 5 caractères
        if not Tournaments.objects.filter(code=code).exists():
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

def default_scoreboards():
    return {'scoreboards': []}
