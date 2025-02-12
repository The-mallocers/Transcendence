from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError

class PongConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pong'

    # def ready(self):
    #     from apps.pong.models import Rank
    #     try:
    #         for r in Ranks:
    #             mmr = 0
    #             if not Rank.objects.filter(name=r.name).exists():
    #                 Rank.objects.create(name=r.name, mmr_min=mmr, mmr_max=mmr+100)
    #                 mmr += 100
    #     except (OperationalError, ProgrammingError):
    #         pass

