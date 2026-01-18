# backend/urls.py - FIXED VERSION (NO EMERGENCY CODE)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="ProjectHub API",
        default_version='v1',
        description="Academic Project Marketplace API Documentation",
        terms_of_service="https://www.projecthub.com/terms/",
        contact=openapi.Contact(email="support@projecthub.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Authentication API
    path('api/auth/', include('accounts.urls')),
    
    # Projects App API
    path('api/projects/', include('projects.urls')),

    # Core App (Web pages)
    path('', include('core.urls')),

    # Payments App API
    path('api/payments/', include('payments.urls')),
    
    # Django Rest Framework auth URLs (for browsable API)
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass