from django.urls import path, include

urlpatterns = [
    path('', include('apps.index.urls')),
    path('new', include("apps.index.urls")),
    path('account/', include("apps.profile.urls")),
    path('auth/', include("apps.auth.urls")),
    path('admin/', include("apps.admin.urls")),
    path('pong/', include('apps.pong.urls')),
    path('error/', include('apps.error.urls')),
    #later, do the thing where 404 is an int and we pass it as context in the template
]