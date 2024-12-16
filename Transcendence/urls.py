from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('auth/', include("authentification.urls")),
    path('account/', include("account.urls")),
    path('', include("index.urls"))
]
