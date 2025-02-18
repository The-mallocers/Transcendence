from django.core.validators import MinLengthValidator, MaxLengthValidator, \
    RegexValidator
from rest_framework import serializers

from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer
from utils.pong.objects import Paddle


class PlayerSerializer(serializers.ModelSerializer):
    paddle = serializers.SerializerMethodField()

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
        fields = ['id', 'nickname', 'paddle']
        read_only_fields = ['id']

    def get_paddle(self, obj):
        paddle = self.context.get('paddle', Paddle())
        return PaddleSerializer(paddle).data