from django.urls import path, re_path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('grafana', views.grafana_proxy, name='grafana_proxy'),
    # re_path(r'^grafana-proxy/(?P<path>.*)$', views.grafana_proxy, name='grafana_proxy'),
    path('register', views.register_get, name='register'),
    path('login', views.login_get, name='login'),
    # path('2fa', views.view_two_fa, name='2fa'),
    # path('2facode', views.post_twofa_code, name='2fa'),
]