from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('pages', include("apps.pages.urls")),

    path('api/auth/', include('apps.auth.api.urls')),
    # ────────────────────────────────────── Api ─────────────────────────────────────── #
    re_path(r'^.*$', TemplateView.as_view(template_name='base.html')),

    # path('api/', include("apps.api.urls")),
    # path('api/auth/', include('apps.auth.api.urls')),
    # path('api/profile/', include('apps.profile.api.urls')),
    # path('api/client/', include('apps.shared.api.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)