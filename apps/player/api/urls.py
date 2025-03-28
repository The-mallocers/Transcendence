from django.urls import path

from apps.player.api.views import PlayerApiView

urlpatterns = [
    path('', PlayerApiView.as_view(), name='player'),
]
