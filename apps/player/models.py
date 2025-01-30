import uuid

from django.db import models
from django.db.models import ManyToManyField, ImageField, ForeignKey
from django.db.models.fields import CharField, IntegerField

class Player(models.Model):
    class Meta:
        db_table = 'client_player'

    # ━━ PRIMARY FIELD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)

    # ━━ PLAYER INFOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # game = GameField() --> Faut voir pour faire un gamefield
    nickname = CharField(max_length=20, null=False, editable=False)
    friends = ManyToManyField('self', symmetrical=False, blank=True, related_name='friends_with')
    firends_requests = ManyToManyField('self', symmetrical=False, blank=True, related_name='invited_by')
    firends_invitations = ManyToManyField('self', symmetrical=False, blank=True, related_name='requested_by')
    mmr = IntegerField(default=100, blank=True)
    rank = ForeignKey('Rank', on_delete=models.SET_NULL, null=True, blank=True)

    # ── Custom ──────────────────────────────────────────────────────────────────────── #
    skin = CharField(max_length=100, null=True) #A voir quel field il faut mettre

    # ── Stats ───────────────────────────────────────────────────────────────────────── #
    game_win = IntegerField(default=0, blank=True)
    game_loose = IntegerField(default=0, blank=True)
    tournament_win = IntegerField(default=0, blank=True)
    tournament_loose = IntegerField(default=0, blank=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ FUNCTION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    def invite_friend(self, invited_player):
        if self != invited_player:
            if self.friends.filter(invited_player).exists():
                raise ValueError(f"Invited {str(invited_player.nickname)} is already your firend.")
            if self.firends_invitations.filter(invited_player).exists():
                raise KeyError(f"{str(invited_player.nickname)} was already invited.")
            if invited_player.firends_requests.filter(self).exists():
                raise KeyError(f"{str(self.nickname)} is already in pending.")
            else:
                self.firends_invitations.add(invited_player)
                invited_player.firends_requests.add(self)
        else:
            raise ValueError("Cannot invite yourself.")

    def accept_friend(self, request_player):
        if self != request_player:
            self.firends_requests.remove(request_player)
            self.friends.add(request_player)
            if self.firends_invitations.filter(request_player).exists():
                self.firends_invitations.remove(request_player)
            if request_player.friends_invitations.filter(self).exists():
                request_player.accept_player(self)
        else:
            raise ValueError("Cannot accept your own invitation.")

    def remove_friend(self, player):
        if self != player:
            if self.friends.filter(player).exists():
                self.friends.remove(player)
                player.friends.remove(self)
            else:
                raise ValueError(f"{str(player.nickname)} is not your friend")

    def get_friends(self):
        return self.friends.all()

    def add_win(self, mmr: int):
        self.game_win += 1
        self.mmr += mmr
        self.rank = Rank.objects.filter(mmr_min__lte=mmr, mmr_max__lte=mmr).first()
        self.save()

    def add_loose(self, mmr: int):
        self.game_loose += 1
        self.mmr -= mmr
        self.rank = Rank.objects.filter(mmr_min__lte=mmr, mmr_max__lte=mmr).first()
        self.save()

class Rank(models.Model):
    class Meta:
        db_table = 'ranks_list'

    name = CharField(primary_key=True, max_length=100, editable=False, null=False)
    icon = ImageField(upload_to='rank_icon/', null=False)
    mmr_min = IntegerField(null=False)
    mmr_max = IntegerField(null=False)