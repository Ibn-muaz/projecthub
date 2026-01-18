# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# === ADD THESE IMPORTS AT THE TOP ===
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

# === EMERGENCY RESET VIEW ===
@csrf_exempt
def emergency_admin_reset(request):
    """
    EMERGENCY ADMIN PASSWORD RESET
    Use this only if you forget your Django admin password.
    Access via: /emergency-reset/?token=YOUR_SECRET_TOKEN
    REMOVE THIS CODE AFTER USE!
    """
    # Secret token for security - you can change this
    SECRET_TOKEN = "projecthub_emergency_2024_reset"
    
    # Get token from URL or form
    token = request.GET.get('token') or request.POST.get('token')
    
    if token != SECRET_TOKEN:
        return HttpResponse(
            '<h1>Access Denied</h1><p>Invalid or missing token.</p>',
            status=403,
            content_type='text/html'
        )
    
    try:
        User = get_user_model()
        
        # Try to get existing admin user
        try:
            admin_user = User.objects.get(username='admin')
            action = "UPDATED"
        except User.DoesNotExist:
            # Create new admin if doesn't exist
            admin_user = User(
                username='admin@2223',
                email='jabaltech1@gmail.com',
                first_name='Admin',
                last_name='User'
            )
            action = "CREATED"
        
        # Set new password - CHANGE THIS AFTER LOGIN!
        new_password = "AdminProjectHub@2223"
        admin_user.set_password(new_password)
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        
        # Success response with credentials
        html_response = f"""
        <html>
        <head><title>Emergency Admin Reset - ProjectHub</title></head>
        <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: 0 auto;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #4CAF50;">✅ Admin Password Reset Successful!</h1>
                <p>Your Django admin access has been restored.</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #4CAF50; margin: 30px 0;">
                <h3>📋 Login Credentials:</h3>
                <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <p><strong>Admin URL:</strong> <a href="/admin/" target="_blank">/admin/</a></p>
                    <p><strong>Username:</strong> <code style="background: #f1f1f1; padding: 5px 10px; border-radius: 3px;">admin</code></p>
                    <p><strong>Password:</strong> <code style="background: #f1f1f1; padding: 5px 10px; border-radius: 3px;">{new_password}</code></p>
                    <p><strong>Status:</strong> <span style="color: #4CAF50;">User {action}</span></p>
                </div>
                <p style="text-align: center; margin-top: 20px;">
                    <a href="/admin/" style="background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        🚀 Go to Admin Login
                    </a>
                </p>
            </div>
            
            <div style="background: #fff3cd; border: 1px solid #ffc107; color: #856404; padding: 20px; border-radius: 5px; margin: 30px 0;">
                <h3>⚠️ CRITICAL SECURITY WARNING:</h3>
                <ol style="line-height: 1.8;">
                    <li><strong>Log in immediately</strong> and change this password!</li>
                    <li><strong>Remove this emergency reset code</strong> from backend/urls.py after use!</li>
                    <li>Consider creating a proper admin account and deleting this temporary one.</li>
                    <li>Never leave this reset endpoint in production code.</li>
                </ol>
            </div>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 14px; color: #666;">
                <p><strong>Note:</strong> This is a one-time emergency reset. The code should be removed from your repository immediately after regaining access.</p>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html_response)
    
    except Exception as e:
        error_html = f"""
        <html>
        <body style="font-family: Arial; padding: 40px;">
            <h1 style="color: #dc3545;">❌ Reset Failed</h1>
            <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Error:</strong> {str(e)}</p>
            </div>
            <p>Check your Django logs for more details.</p>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500)

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
    
    # === ADD THIS LINE FOR EMERGENCY RESET ===
    path('emergency-reset/', emergency_admin_reset, name='emergency_reset'),
    
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