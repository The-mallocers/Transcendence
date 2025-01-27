from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import PasswordSerializer
from ..models import Password


class PasswordViewSet(viewsets.ModelViewSet):
    queryset = Password.objects.all()
    serializer_class = PasswordSerializer

    @action(detail=True, methods=['post'])
    def check_password(self, request, pk=None):
        password_obj = self.get_object()
        password_to_check = request.data.get('password', '')

        if password_obj.check_pwd(password_to_check):
            return Response({'valid': True})
        return Response({'valid': False}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, **kwargs):
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)