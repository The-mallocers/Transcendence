from django.urls import path

from apps.shared.api.views import ClientApiView

urlpatterns = [
    path('', ClientApiView.as_view(), name='client-create'),
]