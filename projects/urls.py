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
    
    # Tools
    path('tools/topic-generator/', views.TopicGeneratorView.as_view(), name='topic-generator-api'),
]