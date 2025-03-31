from django.urls import path

from apps.client.api.views import ClientApiView, GetClientIdApiView

urlpatterns = [
    path('create', ClientApiView.as_view(), name='client-create'),
    path('get-id', GetClientIdApiView.as_view(), name='client-id'),
]
