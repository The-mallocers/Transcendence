from django.apps import AppConfig
from django.db.models.signals import post_migrate


class PongConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pong'


    def ready(self):
        post_migrate.connect(self.populate_ranks, sender=self)

    def populate_ranks(self, **kwargs):
        from apps.pong.models import Rank
        from utils.pong.enums import Ranks

        mmr = 0
        for r in Ranks:
            if not Rank.objects.filter(name=r.name).exists():
                Rank.objects.create(name=r.name, mmr_min=mmr+1, mmr_max=mmr+100)
                mmr += 100

