import random

def generate_unique_code():
    # while True:
    code = random.randint(1000, 9999)
    return code
        # from apps.game.models import GameRoom
        # if not GameRoom.objects.filter(code=code).exists():
        #     return code