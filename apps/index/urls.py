from django.urls import path

from apps.index import view

urlpatterns = [
    path('', view.index_get, name='index'),
]
