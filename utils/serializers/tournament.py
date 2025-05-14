import math

from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from rest_framework import serializers

from utils.enums import TournamentStatus, GameStatus


class TournamentSerializer(serializers.Serializer):
    title = serializers.CharField(
        max_length=40,
        error_messages={'blank': 'Tournament title cannot be empty'}
    )
    #For the future, only validate 4 8 16.
    max_clients = serializers.IntegerField(
        validators=[
            MinValueValidator(2, message="Tournament must have at least 2 players"),
            MaxValueValidator(16, message="Tournament cannot have more than 16 players"),
        ]
    )
    is_public = serializers.BooleanField()
    has_bots = serializers.BooleanField()
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
    host = serializers.UUIDField()

    def validate_max_players(self, value):
        # if value % 4 != 0:
        #     raise ValidationError("Number of maximum players must be a multiple of 4")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['status'] = TournamentStatus.CREATING
        data['created-at'] = timezone.now().isoformat()
        data['clients'] = [str(data['host'])]
        data['scoreboards'] = self.generate_tournament_structure(data['max_clients'])
        return data

    # this will generate a json With all the matches that will be played during the tournament.
    @staticmethod
    def generate_tournament_structure(max_player):
        num_rounds = math.ceil(math.log2(max_player))

        tournament = {
            "num_rounds": num_rounds,
            "current_round": 0,
            "rounds": {}
        }

        for round_num in range(1, num_rounds + 1):
            if round_num == 1:
                matches_in_round = math.ceil(max_player / 2)
            else:
                matches_in_round = 2 ** (num_rounds - round_num)

            tournament["rounds"][f"round_{round_num}"] = {
                "matches_total": matches_in_round,
                "matches_completed": 0,
                "games": {}
            }

            for match_num in range(1, matches_in_round + 1):
                game_id = f"r{round_num}m{match_num}"
                tournament["rounds"][f"round_{round_num}"]["games"][game_id] = {
                    "game_code": "",  # Will be filled when game is created
                    "status": GameStatus.CREATING,
                    # "winner": None,
                    # "loser": None,
                    "winner_username": None,
                    "loser_username": None,
                    "loser_score": 0,
                    "winner_score": 0,
                }

        return tournament
