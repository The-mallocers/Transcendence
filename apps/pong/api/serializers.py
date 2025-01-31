from rest_framework import serializers

from apps.pong.utils import Paddle


class PaddleSerializer(serializers.Serializer):
    width = serializers.FloatField()
    height = serializers.FloatField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    speed = serializers.FloatField()

    def create(self, validated_data):
        return Paddle(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance
