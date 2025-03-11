import logging

from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.admin.api.serializers import GrafanaSerializer
from apps.admin.models import Rights
from apps.shared.models import Clients


class GrafanaTokenApiView(APIView):
    # permission_classes = [GrafanaPermission]

    def get_object(self, pk):
        try:
            return Rights.objects.get(id=pk)
        except Rights.DoesNotExist:
            return None

    def post(self, request, pk, *args, **kwargs):
        grafana_instance = self.get_object(pk)
        self.check_object_permissions(self.request, grafana_instance)

        if not grafana_instance:
            return Response({"grafana_token": ["Grafana token entry not found."]}, status=status.HTTP_404_NOT_FOUND)

        serializer = GrafanaSerializer(grafana_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"grafana_token": {"valid": True, "id": serializer.data.get('id')}},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request: HttpRequest, pk=None, *args, **kwargs):
        logging.info('test')
        # Si un ID est fourni, récupérer un token spécifique
        if pk:
            grafana_instance = self.get_object(pk)
            self.check_object_permissions(self.request, grafana_instance)

            if not grafana_instance:
                return Response({"grafana_token": ["Grafana token entry not found."]},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = GrafanaSerializer(grafana_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Si aucun ID n'est fourni, récupérer tous les tokens auxquels l'utilisateur a accès
        else:
            # Filtrer selon les permissions de l'utilisateur
            client = Clients.get_client_by_id(request.user.id)

            if client.rights.is_admin:
                # Les admins peuvent voir tous les tokens
                grafana_rights = Rights.objects.all()
            else:
                # Les utilisateurs réguliers ne voient que leurs propres tokens
                grafana_rights = Rights.objects.filter(id=client.rights.id)

            serializer = GrafanaSerializer(grafana_rights, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

# class GrafanaIdApiView(APIView):
