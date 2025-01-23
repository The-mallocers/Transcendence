from django.urls import path

from . import views
from .views import error404_get

urlpatterns = [
    path('404', views.error404_get, name='error_404'),
]

handler404 = error404_get
