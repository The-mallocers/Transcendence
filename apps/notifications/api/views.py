from django.http import HttpRequest
from rest_framework import status
from rest_framework.fields import CharField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from apps.client.models import Clients
from utils.enums import RTables
from utils.redis import RedisConnectionPool


class FriendSerializer(ModelSerializer):
    username = CharField(source='profile.username', read_only=True)

    class Meta:
        model = Clients
        fields = ['id', 'username']


class GetFriendsApiView(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        client = Clients.get_client_by_request(request)
        serializer = FriendSerializer(client.friend.friends.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetPendingFriendsApiView(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        client = Clients.get_client_by_request(request)
        serializer = FriendSerializer(client.friend.pending_friends.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetPendingDuelsApiView(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        client = Clients.get_client_by_request(request)
        redis = RedisConnectionPool.get_sync_connection(self.__class__.__name__)
        pending_duels = []
        for duel_hash in redis.scan_iter(match=RTables.HASH_DUEL_QUEUE('*')):
            if redis.hexists(duel_hash, str(client.id)):
                pending_duels.append(duel_hash)
        targets = [redis.hgetall(duel_hash) for duel_hash in pending_duels]
        print(targets)
        serializer = FriendSerializer(Clients.objects.filter(id__in=[x['target'] for x in targets]), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
