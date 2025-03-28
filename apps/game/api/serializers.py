from rest_framework import serializers

from apps.game.models import Game
from apps.pong.api.serializers import BallSerializer
from utils.pong.enums import GameStatus
from utils.pong.objects.ball import Ball


class GameSerializer(serializers.ModelSerializer):
    ball = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    game_id = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['game_id', 'status', 'ball']
        # fields = ['id', 'players', 'ball', 'status', 'timer']

    def get_ball(self, obj):
        ball = Ball()
        return BallSerializer(ball).data

    def get_status(self, obj):
        status = GameStatus(GameStatus.CREATING)
        return status

    def get_game_id(self, obj):
        game_id = self.context.get('id')
        return game_id
