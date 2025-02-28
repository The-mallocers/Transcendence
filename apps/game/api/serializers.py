from rest_framework import serializers

from apps.game.models import Game
from apps.player.models import Player
from apps.pong.api.serializers import BallSerializer
from utils.pong.objects import Ball


class GameSerializer(serializers.ModelSerializer):
    players = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), many=True)  # Permet l'ajout/modif
    ball = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['id', 'players', 'ball', 'status', 'timer']

    def get_ball(self, obj):
        ball = self.context.get('ball')
        return BallSerializer(ball).data