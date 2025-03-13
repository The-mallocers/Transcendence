from django.core.validators import MinLengthValidator, MaxLengthValidator, \
    RegexValidator
from rest_framework import serializers

from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer
from utils.pong.enums import Side


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
        fields = ['id', 'nickname', 'score', 'side', 'paddle']
        read_only_fields = ['id']

    def get_paddle(self, obj):
        paddle = self.context.get('paddle')
        return PaddleSerializer(paddle).data

    def get_side(self, obj):
        side = self.context.get('side', Side.LEFT) #
        #THIS WILL PROBABLY MAKE ALL YOUR PADDLES BE ON THE LEFT BUT THIS CRASHES THE TERMINAL EVERYTIME SOMEONE REGISTERS IF SIDE BY ITSELF
        return side