from django.core.validators import MinLengthValidator, MaxLengthValidator, \
    RegexValidator
from rest_framework import serializers

from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer
from apps.shared.models import Clients
from utils.pong.enums import Side
from apps.game.game import GameManager


class PlayerSerializer(serializers.ModelSerializer):
    paddle = serializers.SerializerMethodField()
    side = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    nickname = serializers.CharField(validators=[
        MinLengthValidator(3),
        MaxLengthValidator(50),
        RegexValidator(
            regex=r'^[a-zA-ZáàäâéèêëíìîïóòôöúùûüçñÁÀÄÂÉÈÊËÍÌÎÏÓÒÔÖÚÙÛÜÇÑ0-9_-]+$',
            message="Username can only contain letters, numbers, and underscores."
        )
    ], required=True)

    class Meta:
        model = Player
        fields = ['id', 'nickname', 'score', 'side', 'paddle']
        read_only_fields = ['id']

    def get_paddle(self, obj):
        paddle = self.context.get('paddle')
        return PaddleSerializer(paddle).data

    def get_side(self, obj):
        side = self.context.get('side', Side.LEFT) #
        return side

    def get_score(self, obj):
        score = self.context.get('score', 0)
        return score


class PlayerInformationSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    player_profile = serializers.SerializerMethodField()
    paddle = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['client_id', 'nickname', 'player_profile', 'paddle']

    def get_paddle(self, obj):
        paddle = self.context.get('paddle')
        return PaddleSerializer(paddle).data

    def get_client_id(self, obj):
        client = Clients.get_client_by_player(self.context.get('id'))
        return str(client.id) if client else None

    def get_player_profile(self, obj):
        client = Clients.get_client_by_player(self.context.get('id'))
        return str(client.profile.profile_picture) if client and client.profile else None

class GameFinishSerializer(serializers.ModelSerializer):
    winner = serializers.SerializerMethodField()
    loser = serializers.SerializerMethodField()
    pL_score = serializers.SerializerMethodField()
    pR_score = serializers.SerializerMethodField()

    class Meta:
        fields = ['winner', 'loser', 'pL_score', 'pR_score']

    def get_winner(self, obj):
        game = GameManager.get_game_db(self.context.get('id'))

