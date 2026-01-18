# projects/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'projects', views.ProjectMaterialViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
    
    # Payment endpoints
    path('payments/init/', views.PaymentInitView.as_view(), name='payments-init'),
    path('payments/verify/', views.PaymentVerifyView.as_view(), name='payments-verify'),
    
    # Download endpoints
    path('downloads/request/', views.DownloadRequestView.as_view(), name='downloads-request'),
    path('downloads/file/<str:token>/', views.DownloadFileView.as_view(), name='downloads-file'),
    
    # User endpoints
    path('me/purchases/', views.StudentPurchaseListView.as_view(), name='me-purchases'),
    path('me/downloads/', views.StudentDownloadListView.as_view(), name='me-downloads'),
    
    # Admin endpoints
    path('admin/stats/overview/', views.AdminStatsOverviewView.as_view(), name='admin-stats-overview'),
    
    # Topic Generator endpoints
    path('tools/topic-generator/', views.TopicGeneratorView.as_view(), name='topic-generator-api'),
    path('tools/departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('tools/save-topics/', views.SaveTopicsView.as_view(), name='save-topics'),
    path('tools/saved-topics/', views.GetSavedTopicsView.as_view(), name='get-saved-topics'),
    path('tools/topic-statistics/', views.TopicStatisticsView.as_view(), name='topic-statistics'),
    
    # Project tools
    path('tools/', views.ProjectToolsView.as_view(), name='project-tools'),
      # Emergency admin reset (remove after use!)
    path('emergency-reset/', views.emergency_admin_reset, name='emergency_reset'),
]