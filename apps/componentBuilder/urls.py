from django.urls import path

from . import views

urlpatterns = [
    path('', views.editMode, name='edit'),
    path('save-component', views.saveComponent),
    path('get-component/<int:component_id>', views.getComponent),
]
