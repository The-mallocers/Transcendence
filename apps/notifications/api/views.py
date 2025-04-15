from django.http import HttpRequest
from rest_framework import status
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from apps.client.models import Clients
from apps.notifications.models import Friend


class FriendsSerializer(ModelSerializer):
    friends = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Friend
        fields = 'friends'


class PendingFriendsSerializer(ModelSerializer):
    pending_friends = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Friend
        fields = 'pending_friends'


class GetFriendsApiView(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        client = Clients.get_client_by_request(request)
        serializer = FriendsSerializer(client.friend, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetPendingFriendsApiView(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        return Response({
            "client_id"
        }, status=status.HTTP_200_OK)
