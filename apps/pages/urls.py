from django.urls import path, include

urlpatterns = [
    path('', include('apps.index.urls')),
    path('new', include("apps.index.urls")),
    path('account/', include("apps.profile.urls")),
    path('auth/', include("apps.auth.urls")),
    path('admin/', include("apps.admin.urls")),
    path('pong/', include('apps.pong.urls')),
    path('error/', include('apps.error.urls')),
    path('chat/', include('apps.chat.urls')),
]