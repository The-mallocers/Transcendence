from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register_post, name='register'),
    path('login', views.login_post, name='login'),
    path('logout', views.logout, name='logout'),
    path('change_two_fa', views.change_two_fa, name='two_fa')
]
