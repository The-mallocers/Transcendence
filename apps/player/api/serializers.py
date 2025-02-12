from rest_framework import serializers

from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer
from utils.pong.objects import Paddle


class PlayerSerializer(serializers.ModelSerializer):
    paddle = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['id', 'paddle']
        read_only_fields = ['id']

    def get_paddle(self, obj):
        paddle = self.context.get('paddle', Paddle())
        return PaddleSerializer(paddle).data