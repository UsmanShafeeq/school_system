from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin site URL
    path('accounts/', include('apps.accounts.urls')),  # Include accounts app URLs
    path('', include('apps.core.urls')),  # Include core app URLs (home and dashboards)
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)