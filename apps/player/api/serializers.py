from django.core.validators import MinLengthValidator, MaxLengthValidator, \
    RegexValidator
from rest_framework import serializers

from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer
from utils.pong.enums import Side
from utils.pong.objects import Paddle


class PlayerSerializer(serializers.ModelSerializer):
    paddle = serializers.SerializerMethodField()
    side = serializers.SerializerMethodField()
    score = serializers.IntegerField(default=0)

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
        fields = ['id', 'nickname', 'side', 'score', 'paddle']
        read_only_fields = ['id']

    def get_paddle(self, obj):
        paddle = self.context.get('paddle', Paddle())
        return PaddleSerializer(paddle).data

    def get_side(self, obj):
        side = self.context.get('side', Side)
        return side