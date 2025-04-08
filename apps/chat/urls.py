from django.urls import path

from apps.chat import view
from . import views

urlpatterns = [
    path('', view.chat_get, name='chat'),
    path('friendrequest/', views.friendrequest)
]
