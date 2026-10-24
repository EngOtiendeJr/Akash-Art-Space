from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from main.admin import akash_admin_site

urlpatterns = [
    path("admin/", akash_admin_site.urls),
    path("", include("main.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
