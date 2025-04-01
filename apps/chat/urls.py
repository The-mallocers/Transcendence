from django.urls import path

from apps.chat import view

urlpatterns = [
    path('', view.chat_get, name='chat')
]
