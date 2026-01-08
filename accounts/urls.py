# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # API URLs (JWT Authentication)
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('me/', views.MeView.as_view(), name='auth-me'),
    # Comment out if EmailVerificationToken doesn't exist
    # path('verify-email/', views.VerifyEmailView.as_view(), name='auth-verify-email'),
    
    # Web URLs (Session Authentication - for web pages)
    path('web/login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='web-login'),
    path('web/logout/', auth_views.LogoutView.as_view(next_page='/'), name='web-logout'),
    path('web/register/', views.web_register_view, name='web-register'),
    path('web/profile/', views.web_profile_view, name='web-profile'),
]