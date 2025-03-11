from rest_framework import serializers

from apps.admin.models import Rights


class GrafanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rights
        fields = ['grafana_id', 'grafana_token']
