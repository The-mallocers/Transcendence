import re

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
        duel_data = []

        for duel_hash in redis.scan_iter(match=RTables.HASH_DUEL_QUEUE('*')):
            if redis.hexists(duel_hash, str(client.id)):
                duel_info = redis.hgetall(duel_hash)
                target_id = None
                for key, value in duel_info.items():
                    if value == b'True':
                        target_id = key.decode('utf-8')
                        break
                target_client = Clients.objects.get(id=target_id)
                duel_data.append({
                    'id': str(target_client.id),
                    'username': target_client.profile.username,
                    'duel_id': re.search(rf'{RTables.HASH_DUEL_QUEUE("")}(\w+)$', duel_hash.decode('utf-8')).group(1)
                })

        return Response(duel_data, status=status.HTTP_200_OK)

class GetUserName(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        client = Clients.get_client_by_request(request)
        if client:
            return Response({
                "status": "success",
                "data": {
                    "username": client.profile.username
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Client not found"
            }, status=status.HTTP_404_NOT_FOUND)

import json

class GetImages(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        opponent = request.GET.get('opponent')
        client = Clients.get_client_by_request(request)
        target = Clients.get_client_by_username(opponent)
        
        duelExist = False
        
        redis = RedisConnectionPool.get_sync_connection("get_duel")
        for duel in redis.scan_iter(match=RTables.HASH_DUEL_QUEUE('*')):
            if redis.hexists(duel, str(client.id)) and redis.hexists(duel, str(target.id)):
                duelExist = True
                
        if client and target:
            return Response({
                "status": "success",
                "data": {
                    "hostPicture": client.profile.profile_picture.url,
                    "opponentPicture": target.profile.profile_picture.url,
                    "duelExist": duelExist
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Client or opponent not found",
                "data":{
                    "duelExist" : duelExist,
                }
            }, status=status.HTTP_404_NOT_FOUND)