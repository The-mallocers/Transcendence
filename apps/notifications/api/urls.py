from django.urls import path

from apps.notifications.api.views import GetFriendsApiView, GetPendingFriendsApiView

urlpatterns = [
    path('get_friends/', GetFriendsApiView.as_view(), name='friend'),
    path('get_pending_friends/', GetPendingFriendsApiView.as_view(), name='pending_friends'),
]
