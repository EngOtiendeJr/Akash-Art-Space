from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.static import serve
from main.admin import akash_admin_site

urlpatterns = [
    path("admin/", akash_admin_site.urls),
    path("", include("main.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Uploaded media lives on the Render disk (MEDIA_ROOT), not in staticfiles.
    urlpatterns += [
        path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
