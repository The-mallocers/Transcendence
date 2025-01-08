from django.urls import path

from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('edit', views.editMode),
    path('save-component', views.saveComponent),
    path('get-component/<int:component_id>', views.getComponent),
]
