from django.urls import path

from error.views import error404_get
from . import views

urlpatterns = [
    path('', views.index_get, name='index'),
]

handler404 = error404_get
