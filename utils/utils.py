import random
import re


def generate_unique_code():
    from apps.game.models import Game
    while True:
        code = random.randint(1000, 9999)
        if not Game.objects.filter(id=code).exists():
            return code

def generate_valid_group_name(player_id):
    # Convert the UUID to a valid string format
    valid_name = str(player_id)  # player_id could be a UUID instance
    # Ensure the string contains only valid characters (alphanumeric, hyphens, underscores, periods)
    valid_name = re.sub(r'[^a-zA-Z0-9._-]', '_', valid_name)
    if len(valid_name) > 100:
        raise ValueError("Group name is too long")
    return valid_name