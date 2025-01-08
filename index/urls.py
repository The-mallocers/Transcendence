from django.urls import path

from error.views import error_404
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

handler404 = error_404