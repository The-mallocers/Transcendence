from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class PlayerApiView(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        token = request.COOKIES.get('access_token')

        # il faut decoder le jwt

        return Response({
            "player_id": token
        }, status=status.HTTP_200_OK)
