from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from apps.client.models import Clients


class FriendSerializer(ModelSerializer):
    class Meta:
        model = Clients
        fields = ['id']


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
