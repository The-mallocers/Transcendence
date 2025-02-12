import redis

from apps.player.api.serializers import PlayerSerializer

redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class PlayerManager:
    @classmethod
    def get_player(cls, player_id):
        player_data = redis.get(f"pong:players:{player_id}")

        if player_data:
            serializer = PlayerSerializer(data=player_data)

            if serializer.is_valid():
                return serializer.validated_data
        else:
            return None

    @classmethod
    def get_player_list(cls):
        return redis.smembers("pong:list:players")

    @classmethod
    def delete_player(cls, player_id):
        key = f"pong:players:{player_id}"
        redis.delete(key)
        redis.srem("pong:list:players", player_id)