from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth.api.permissions import PasswordPermission
from apps.auth.api.serializers import PasswordSerializer
from apps.auth.models import Password


class PasswordUpdateView(APIView):
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