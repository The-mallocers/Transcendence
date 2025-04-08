from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.enums import JWTType
from utils.jwt.JWT import extract_token
from utils.jwt.JWTGenerator import JWTGenerator
from utils.serializers.client import ClientSerializer


class ClientApiView(APIView):
    authentication_classes = []

    # permission_classes = [ClientPermission]

    def post(self, request, *arg, **kwargs):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetClientIdApiView(APIView):
    def get(self, request: HttpRequest, *args, **kwargs):
        token = extract_token(request.COOKIES, JWTType.ACCESS)

        return Response({
            "client_id": token.SUB
        }, status=status.HTTP_200_OK)
