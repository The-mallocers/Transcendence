from django.core.validators import MinLengthValidator, MaxLengthValidator, \
    RegexValidator
from rest_framework import serializers

from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer
from apps.shared.models import Clients
from utils.pong.enums import Side
from utils.pong.objects.paddle import Paddle
from utils.pong.objects import PADDLE_WIDTH, CANVAS_WIDTH, OFFSET_PADDLE
from utils.pong.enums import Side

class PlayerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    paddle = serializers.SerializerMethodField()
    side = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['id', 'score', 'side', 'paddle']

    def get_paddle(self, obj):
        paddle = self.context.get('paddle')
        return PaddleSerializer(paddle).data

    def get_side(self, obj):
        side = self.context.get('side', Side.LEFT)
        return side

    def get_score(self, obj):
        score = self.context.get('score', 0)
        return score
    
    def get_id(self, obj):
        id = self.context.get('id')
        return id


class PlayerInformationSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    player_profile = serializers.SerializerMethodField()
    paddle = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['client_id', 'player_profile', 'paddle']

    def get_paddle(self, obj):
        paddle = self.context.get('paddle')
        return PaddleSerializer(paddle).data

    def get_client_id(self, obj):
        client = Clients.get_client_by_player(self.context.get('id'))
        return str(client.id) if client else None

    def get_player_profile(self, obj):
        client = Clients.get_client_by_player(self.context.get('id'))
        return str(client.profile.profile_picture) if client and client.profile else None

class PlayersRedisSerializer(serializers.ModelSerializer):
    player_left = PlayerSerializer()
    player_right = PlayerSerializer()

    class Meta:
        model = Player
        fields = ['player_left', 'player_right']

    def to_representation(self, instance):
        paddle_left = Paddle(OFFSET_PADDLE)
        paddle_right = Paddle(CANVAS_WIDTH - OFFSET_PADDLE - PADDLE_WIDTH)
        return {
            'player_left': PlayerSerializer(instance.get('player_left'), context={'paddle': paddle_left, 'side': Side.LEFT, 'id': str(instance.get('player_left').class_client.id)}).data,
            'player_right': PlayerSerializer(instance.get('player_right'), context={'paddle': paddle_right, 'side': Side.RIGHT, 'id': str(instance.get('player_right').class_client.id)}).data
        }

    

class GameFinishSerializer(serializers.ModelSerializer):
    winner = serializers.SerializerMethodField()
    loser = serializers.SerializerMethodField()
    pL_score = serializers.SerializerMethodField()
    pR_score = serializers.SerializerMethodField()

    class Meta:
        fields = ['winner', 'loser', 'pL_score', 'pR_score']

    def get_winner(self, obj):
        from utils.threads.game import GameManager
        game = GameManager.get_game_db(self.context.get('id'))

