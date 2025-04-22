from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
import math
from utils.enums import TournamentStatus
from django.utils import timezone

#Left to add 
# - name -> Ptit nom par default a priori ?
# - host -> Aucune idee de comment je choppe ca
# - Players -> Une liste avec excatement assez de slots par rapport a max players ?


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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['scoreboards'] = self.generate_tournament_structure(data['max_players'])
        data['status'] = TournamentStatus.CREATING
        data['created-at'] = timezone.now() 
        return data

    
    #this will generate a json With all the matches that will be played during the tournament.
    def generate_tournament_structure(max_players):
        num_rounds = math.ceil(math.log2(max_players))

        tournament = {
            "rounds": []
        }

        for round_num in range(1, num_rounds + 1):
            if round_num == 1:
                matches_in_round = math.ceil(max_players / 2)
            else:
                matches_in_round = 2 ** (num_rounds - round_num)
            
            round_data = {
                "roundNumber": round_num,
                "matches": []
            }
            
            for match_num in range(1, matches_in_round + 1):
                match = {
                    "matchId": f"{round_num}.{match_num}",
                    "player1": {
                        "id": "",
                        "name": ""
                    },
                    "player2": {
                        "id": "",
                        "name": ""
                    },
                    "score": {
                        "player1": 0,
                        "player2": 0
                    },
                    "winner": "",
                    "completed": False
                }
                round_data["matches"].append(match)
            
            tournament["rounds"].append(round_data)

        return tournament
    
    