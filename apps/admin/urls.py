from django.urls import path

from . import views

urlpatterns = [
    path('', views.admin_get, name='admin'),
    path('user/<uuid:client_id>', views.edit_user_get, name='user_edit')
]