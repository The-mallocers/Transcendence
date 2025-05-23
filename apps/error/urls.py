from django.urls import path

from . import views
from django.conf.urls import handler404

handler404 = 'views.error'

urlpatterns = [
    path('<int:error_code>/', views.error, name='error'),
]
