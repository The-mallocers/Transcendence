from django.urls import path, include
from django.views.generic import TemplateView

from apps.index.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
]