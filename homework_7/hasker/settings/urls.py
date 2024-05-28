from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("my_hasker/", include("my_hasker.urls")),
    path("admin/", admin.site.urls),
]