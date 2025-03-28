from django.db import models
from django.db.models import CharField, ImageField, IntegerField

from utils.pong.enums import Ranks


class Rank(models.Model):
    class Meta:
        db_table = 'ranks_list'

    name = CharField(primary_key=True, max_length=15, editable=False, null=False,
                     choices=[(ranks.name, ranks.value) for ranks in Ranks])
    icon = ImageField(upload_to='rank_icon/', null=False)
    mmr_min = IntegerField(null=False)
    mmr_max = IntegerField(null=False)
