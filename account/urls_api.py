from django.urls import path

from . import views

urlpatterns = [
    path('update', views.account_post, name='account_update'),
    path('', views.account_delete, name='account_delete')
]
