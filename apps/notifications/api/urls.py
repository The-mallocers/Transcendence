from django.urls import path

from apps.notifications.api.views import GetFriendsApiView, GetPendingFriendsApiView, GetPendingDuelsApiView, GetOnlineStatus

urlpatterns = [
    path('get_friends/', GetFriendsApiView.as_view(), name='friend'),
    path('get_pending_friends/', GetPendingFriendsApiView.as_view(), name='pending_friends'),
    path('get_pending_duels/', GetPendingDuelsApiView.as_view(), name='pending_duels'),
    path('get_online_status/', GetOnlineStatus.as_view(), name='online_status'),
]
