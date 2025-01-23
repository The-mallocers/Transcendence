from django.urls import path
from . import views

urlpatterns = [
    path('', views.indexspa, name='indexspa'),
    path('partial/<int:partial_id>', views.partial, name='partial'),
]
