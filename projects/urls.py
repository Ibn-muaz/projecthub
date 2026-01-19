# projects/urls.py (UPDATED - COMPLETE VERSION)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'projects', views.ProjectMaterialViewSet, basename='project')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Payment endpoints
    path('api/payments/init/', views.PaymentInitView.as_view(), name='payments-init'),
    path('api/payments/verify/', views.PaymentVerifyView.as_view(), name='payments-verify'),
    
    # Download endpoints
    path('api/downloads/request/', views.DownloadRequestView.as_view(), name='downloads-request'),
    path('api/downloads/file/<str:token>/', views.DownloadFileView.as_view(), name='downloads-file'),
    
    # User endpoints
    path('api/me/purchases/', views.StudentPurchaseListView.as_view(), name='me-purchases'),
    path('api/me/downloads/', views.StudentDownloadListView.as_view(), name='me-downloads'),
    
    # Admin endpoints
    path('api/admin/stats/overview/', views.AdminStatsOverviewView.as_view(), name='admin-stats-overview'),
    
    # Topic Generator endpoints
    path('api/tools/topic-generator/', views.TopicGeneratorView.as_view(), name='topic-generator-api'),
    path('api/tools/departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('api/tools/save-topics/', views.SaveTopicsView.as_view(), name='save-topics'),
    path('api/tools/saved-topics/', views.GetSavedTopicsView.as_view(), name='get-saved-topics'),
    path('api/tools/topic-statistics/', views.TopicStatisticsView.as_view(), name='topic-statistics'),
    
    # Project tools
    path('api/tools/', views.ProjectToolsView.as_view(), name='project-tools'),
    
    # Emergency admin reset (remove after use!)
    path('api/emergency-reset/', views.emergency_admin_reset, name='emergency_reset'),
    
    # =============== FRONTEND PAGES ===============
    # Static pages (for footer links)
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy-page'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about-page'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms-page'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact-page'),
    
    # Feature pages (from navigation)
    path('projects/', TemplateView.as_view(template_name='project_list.html'), name='project-list-page'),
    path('topic-generator/', TemplateView.as_view(template_name='topic_generator.html'), name='topic-generator-page'),
    
    # Dashboard pages
    path('dashboard/', TemplateView.as_view(template_name='student_dashboard.html'), name='student-dashboard'),
    path('admin/dashboard/', TemplateView.as_view(template_name='admin_dashboard.html'), name='admin-dashboard'),
    
    # Authentication pages
    path('login/', TemplateView.as_view(template_name='login.html'), name='login-page'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register-page'),
    # Logout view (handles POST only)
    path('logout/', LogoutView.as_view(next_page='landing'), name='logout-page'),
    
    # Landing page (homepage)
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
]