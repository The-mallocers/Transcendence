from django.urls import path

from apps.admin import view

urlpatterns = [ 
    path('monitoring/', view.get, name='monitoring'), 
]