from django.urls import path, include

urlpatterns = [
    path('', include('apps.index.urls')),

    # ────────────────────────────────────── Api ─────────────────────────────────────── #

    path('api/auth/', include('apps.auth.api.urls'))
]