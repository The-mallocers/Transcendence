from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers


class TournamentArgsSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=40,
        error_messages={'blank': 'Tournament name cannot be empty'}
    )
    max_players = serializers.IntegerField(
        validators=[
            MinValueValidator(2, message="Tournament must have at least 2 players"),
            MaxValueValidator(16, message="Tournament cannot have more than 16 players")
        ]
    )
    public = serializers.BooleanField()
    bots = serializers.BooleanField()
    points_to_win = serializers.IntegerField(
        validators=[
            MinValueValidator(1, message="Points to win must be at least 1"),
            MaxValueValidator(21, message="Points to win cannot exceed 21")
        ]
    )
    timer = serializers.IntegerField(
        validators=[
            MinValueValidator(30, message="Timer must be at least 30 seconds"),
            MaxValueValidator(600, message="Timer cannot exceed 600 seconds (10 minutes)")
        ]
    )

    def validate(self, data):
        if data.get('max_players') % 2 != 0:
            raise serializers.ValidationError("Maximum players must be an even number")
        return data


class TournamentDataSerializer(serializers.Serializer):
    action = serializers.CharField(
        error_messages={'blank': 'Action cannot be empty'}
    )
    args = TournamentArgsSerializer()

    def validate_action(self, value):
        valid_actions = ['create_tournament']  # Might need to udpate this
        if value not in valid_actions:
            raise serializers.ValidationError(f"Action must be one of: {', '.join(valid_actions)}")
        return value


class TournamentSerializer(serializers.Serializer):
    event = serializers.CharField(
        error_messages={'blank': 'Event type cannot be empty'}
    )
    data = TournamentDataSerializer()

    def validate_event(self, value):
        if value != 'tournament':
            raise serializers.ValidationError("Event type must be 'tournament'")
        return value

    def validate(self, data):
        return data

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        return validated_data
