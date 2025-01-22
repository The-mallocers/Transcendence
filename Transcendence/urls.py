from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from error.views import error_404

urlpatterns = [
    path('', include("index.urls")),
    path('account/', include("account.urls")),
    path('api/', include("api.urls")),
    path('auth/', include("auth.urls")),
    path('admin/', include("admin.urls")),
    path('pong/', include('pong.urls')),
    path('edit/', include("componentBuilder.urls"))
]

handler404 = error_404
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
