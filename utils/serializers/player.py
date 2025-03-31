from rest_framework import serializers

from apps.player.models import Player
from utils.enums import Side
from utils.pong.objects import PADDLE_WIDTH, CANVAS_WIDTH, OFFSET_PADDLE
from utils.pong.objects.paddle import Paddle
from utils.serializers.game import PaddleSerializer


class PlayerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    paddle = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['id', 'score', 'paddle']

    def get_paddle(self, obj):
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
        return instance.client_id

    def get_username(self, instance):
        return instance.class_client.profile.username

    def get_player_profile(self, instance):
        return instance.class_client.profile.profile_picture.url

    def get_paddle(self, instance):
        side = self.context.get('side')
        game_id = self.context.get('game_id')
        player_id = instance.id

        # Create Paddle with necessary context
        x = self._get_paddle_x(side)
        paddle = Paddle(
            game_id=game_id,
            player_id=player_id,
            x=x
        )

        return PaddleSerializer(paddle).data

    def _get_paddle_x(self, side):
        if side is Side.LEFT:
            return OFFSET_PADDLE
        elif side is Side.RIGHT:
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
        pl = instance.get('player_left')
        pr = instance.get('player_right')
        return {
            'player_left': PlayerSerializer(pl, context={'paddle': paddle_left, 'id': str(pl.client_id)}).data,
            'player_right': PlayerSerializer(pr, context={'paddle': paddle_right, 'id': str(pr.client_id)}).data
        }


class GameFinishSerializer(serializers.ModelSerializer):
    winner = serializers.SerializerMethodField()
    loser = serializers.SerializerMethodField()
    pL_score = serializers.SerializerMethodField()
    pR_score = serializers.SerializerMethodField()

    class Meta:
        fields = ['winner', 'loser', 'pL_score', 'pR_score']

    def get_winner(self, obj):
        from utils.threads.game import GameManager
        game = GameManager.get_game_db(self.context.get('id'))
