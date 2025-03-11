from django.urls import path

from . import views

urlpatterns = [
    path('grafana_token/', views.GrafanaTokenApiView.as_view(), name='grafana_token'),
]
