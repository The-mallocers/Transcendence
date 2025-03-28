from django.urls import path

from . import views

urlpatterns = [
    path('', views.profile_get, name='profile'),
    path('settings/', views.settings_get, name='settings'),
    # path('user/<int:username>/', views.profile_get, name='settings'),
]
