from rest_framework import serializers

from apps.game.models import Game
from utils.enums import GameStatus
from utils.pong.objects import paddle, ball
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


class PaddleSerializer(serializers.Serializer):
    width = serializers.FloatField()
    height = serializers.FloatField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    speed = serializers.FloatField()
    move = serializers.CharField()

    def create(self, validated_data):
        return paddle(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class BallSerializer(serializers.Serializer):
    radius = serializers.FloatField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    dx = serializers.FloatField()
    dy = serializers.FloatField()

    def create(self, validated_data):
        return ball(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance
