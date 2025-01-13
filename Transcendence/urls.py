from django.urls import path, include

from error.views import error_404

urlpatterns = [
    path('', include("index.urls")),
    path('api/', include("api.urls")),
    path('account/', include("account.urls")),
    path('admin/', include("admin.urls")),
    path('pong/', include('pong.urls')),
    path('edit/', include("componentBuilder.urls"))
]

handler404 = error_404


