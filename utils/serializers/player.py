from rest_framework import serializers

from apps.player.models import Player
from utils.enums import PlayerSide
from utils.pong.objects import PADDLE_WIDTH, CANVAS_WIDTH, OFFSET_PADDLE
from utils.pong.objects.paddle import Paddle


class PlayerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    paddle = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['id', 'score', 'paddle']

    def get_paddle(self, obj):
        from utils.serializers.game import PaddleSerializer
        paddle = self.context.get('paddle')
        return PaddleSerializer(paddle).data

    def get_score(self, obj):
        score = self.context.get('score', 0)
        return score

    def get_id(self, obj):
        id = self.context.get('id')
        return id


from rest_framework import serializers


# Uncomment this when we will have player stats + the name of client within client model.
class PlayerInformationSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    player_profile = serializers.SerializerMethodField()
    paddle = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['client_id', 'username', 'player_profile', 'paddle']

    def get_client_id(self, instance):
        return str(instance.client.id)

    def get_username(self, instance):
        return instance.client.profile.username

    def get_player_profile(self, instance):
        return instance.client.profile.profile_picture.url

    def get_paddle(self, instance):
        from utils.serializers.game import PaddleSerializer
        side = self.context.get('side')
        game_id = self.context.get('game_id')
        player_id = str(instance.id)

        # Create Paddle with necessary context
        x = self._get_paddle_x(side)
        paddle = Paddle(
            game_id=game_id,
            client_id=player_id,
            x=x
        )

        return PaddleSerializer(paddle).data

    def _get_paddle_x(self, side):
        if side is PlayerSide.LEFT:
            return OFFSET_PADDLE
        elif side is PlayerSide.RIGHT:
            return CANVAS_WIDTH - OFFSET_PADDLE - PADDLE_WIDTH
        return None  # or a default value


class PlayersRedisSerializer(serializers.ModelSerializer):
    player_left = PlayerSerializer()
    player_right = PlayerSerializer()

    class Meta:
        model = Player
        fields = ['player_left', 'player_right']

    def to_representation(self, instance):
        paddle_left = Paddle(x=OFFSET_PADDLE)
        paddle_right = Paddle(x=CANVAS_WIDTH - OFFSET_PADDLE - PADDLE_WIDTH)
        pl = instance.get(PlayerSide.LEFT)
        pr = instance.get(PlayerSide.RIGHT)
        return {
            PlayerSide.LEFT: PlayerSerializer(pl, context={'paddle': paddle_left, 'id': str(pl.client.id)}).data,
            PlayerSide.RIGHT: PlayerSerializer(pr, context={'paddle': paddle_right, 'id': str(pr.client.id)}).data
        }

class PlayerScoreSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    client_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    matches_played = serializers.SerializerMethodField()
    matches_won = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['position', 'client_id', 'username', 'matches_played', 'matches_won', 'points']

    def get_position(self, obj):
        return self.context.get('position')

    def get_client_id(self, obj):
        return self.context.get('client_id')

    def get_username(self, obj):
        return self.context.get('username')

    def get_matches_played(self, obj):
        return self.context.get('matches_played')

    def get_matches_won(self, obj):
        return self.context.get('matches_won')

    def get_points(self, obj):
        return self.context.get('points')
