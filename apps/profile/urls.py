from django.urls import path

from apps.profile import view

urlpatterns = [
    path('', view.profile_get, name='profile'),
    path('settings/', view.settings_get, name='settings'),
    # path('user/<int:username>/', views.profile_get, name='settings'),
]
