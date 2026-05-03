from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("backend.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
