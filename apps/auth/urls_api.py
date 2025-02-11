from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register_post, name='register_api'),
    path('login', views.login_post, name='login_api'),
    path('logout', views.logout, name='logout_api'),
    # path('change_two_fa', views.change_two_fa, name='two_fa')
]
