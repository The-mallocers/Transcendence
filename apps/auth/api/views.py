from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth.api.permissions import PasswordPermission
from apps.auth.api.serializers import PasswordSerializer
from apps.auth.models import Password
from apps.shared.api.serializers import ClientSerializer
from apps.shared.models import Clients
from utils.jwt.JWT import JWTType
from utils.jwt.JWTGenerator import JWTGenerator


class PasswordApiView(APIView):
    permission_classes = [PasswordPermission]

    def get_object(self, pk):
        try:
            return Password.objects.get(id=pk)
        except Password.DoesNotExist:
            return None

    def patch(self, request, pk, *args, **kwargs):
        password_instance = self.get_object(pk)
        self.check_object_permissions(self.request, password_instance)

        if not password_instance:
            return Response({"password": ["Password entry not found."]}, status=status.HTTP_404_NOT_FOUND)

        serializer = PasswordSerializer(password_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"password": {"valid": True, "id": serializer.data.get('id')}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterApiView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = ClientSerializer(data=request.data)

        if serializer.is_valid():
            client = serializer.save()
            return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginApiView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request: HttpRequest, *args, **kwargs):
        email = request.POST.get('email')
        pwd = request.POST.get('password')
        client = Clients.get_client_by_email(email)

        if client is None or client.password.check_pwd(password=pwd) is False:
            return Response({
                "error": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            response = Response({
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
            JWTGenerator(client, JWTType.ACCESS).set_cookie(response)
            JWTGenerator(client, JWTType.REFRESH).set_cookie(response)
            return response
        
class LogoutApiView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request: HttpRequest, *args, **kwargs):
        if request.COOKIES.get('access_token') is not None:
            response = Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        else:
            return Response({
                "error": "You are not log"
            }, status=status.HTTP_401_UNAUTHORIZED)

