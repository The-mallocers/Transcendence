from django.urls import path

from apps.shared.api.views import ClientCreateView

urlpatterns = [
    path('', ClientCreateView.as_view(), name='client-create'),
]