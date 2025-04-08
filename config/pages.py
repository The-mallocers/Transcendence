from django.urls import path, include

urlpatterns = [
    path('', include('apps.index.urls')),
    path('new', include("apps.index.urls")),
    path('account/', include("apps.profile.urls")),
    path('auth/', include("apps.auth.urls")),
    path('pong/', include('apps.game.urls')),
    path('error/', include('apps.error.urls')),
    path('chat/', include('apps.chat.urls')),
    path('profile/', include('apps.profile.urls')),
    path('tournaments/', include('apps.tournaments.urls'))
]
