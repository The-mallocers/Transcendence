from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shared.api.permissions import ClientPermission
from apps.shared.api.serializers import ClientSerializer
from apps.shared.models import Clients


class ClientCreateView(APIView):
    authentication_classes = []
    # permission_classes = [ClientPermission]

    def post(self, request, *arg, **kwargs):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)