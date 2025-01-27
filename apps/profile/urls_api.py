from django.urls import path

from . import views

urlpatterns = [
    path('update/<uuid:client_id>', views.account_post, name='profile_update'),
    path('delete/<uuid:client_id>', views.account_delete, name='profile_delete')
]
