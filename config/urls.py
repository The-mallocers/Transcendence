from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('', include('apps.home.urls')),
    path('new', include("apps.index.urls")),
    path('account/', include("apps.profile.urls")),
    path('auth/', include("apps.auth.urls")),
    path('admin/', include("apps.admin.urls")),
    path('pong/', include('apps.pong.urls')),
    path('edit/', include("apps.componentBuilder.urls")),

    # ────────────────────────────────────── Api ─────────────────────────────────────── #

    path('api/auth/', include('apps.auth.api.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)