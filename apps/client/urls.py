from django.urls import path

from . import views

urlpatterns = [
    # ...existing code...
    path('api/friends/get_pending_tournament_invitations/', views.get_pending_tournament_invitations, name='get_pending_tournament_invitations'),
    # ...existing code...
]