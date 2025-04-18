from django.urls import path

from apps.notifications.api.views import GetFriendsApiView, GetPendingFriendsApiView, GetPendingDuelsApiView

urlpatterns = [
    path('get_friends/', GetFriendsApiView.as_view(), name='friend'),
    path('get_pending_friends/', GetPendingFriendsApiView.as_view(), name='pending_friends'),
    path('get_pending_duels/', GetPendingDuelsApiView.as_view(), name='pending_duels'),
]
