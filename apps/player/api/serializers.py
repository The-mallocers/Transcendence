from rest_framework import serializers

from apps.player.models import Player
from apps.pong.api.serializers import PaddleSerializer


class PlayerSerializer(serializers.ModelSerializer):
    paddle = PaddleSerializer()

    class Meta:
        model = Player
        fields = ['id', 'paddle']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = str(instance.id).replace('-','')  # Enlève les tirets
        return representation