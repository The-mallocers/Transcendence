from django.urls import path
from . import views

urlpatterns = [
    path('<int:error_code>/', views.error, name='error'),
]