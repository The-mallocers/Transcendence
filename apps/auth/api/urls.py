from django.urls import path

from apps.auth.api.views import PasswordApiView, LoginApiView, RegisterApiView, LogoutApiView, GetClientIDApiView, UploadPictureApiView, \
    UpdateApiView, DeleteApiView
from . import views

urlpatterns = [
    path('password/<str:pk>/', PasswordApiView.as_view(), name='password'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('register/', RegisterApiView.as_view(), name='register'),
    path('update/', UpdateApiView.as_view(), name='update'),
    path('logout/', LogoutApiView.as_view(), name='logout'),
    path('getId/', GetClientIDApiView.as_view(), name='getId'),
    path('change_two_fa', views.change_two_fa, name='two_fa'),
    path('2facode', views.post_twofa_code, name='2fa'),
    path('check2faqrcode', views.post_check_qrcode, name='checkqrcode'),
    path('upload_picture/', UploadPictureApiView.as_view(), name='picture'),
    path('delete_account/', DeleteApiView.as_view(), name='delete_account'),
]
