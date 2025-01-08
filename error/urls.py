from django.urls import path
from django.views.generic import RedirectView

from . import views
from .views import error_404

urlpatterns = [
    path('404', views.error_404, name='error_404'),
]

handler404 = error_404