# core/urls.py - UPDATED WITH ALL URL PATTERNS
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # Authentication (web)
    path('login/', views.login_page, name='login-page'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout-page'),
    path('register/', views.register_page, name='register-page'),
    
    # Projects
    path('projects/', views.project_list, name='project-list-page'),
    path('projects/<slug:slug>/', views.project_detail, name='project-detail'),
    
    # Dashboard
    path('dashboard/', views.student_dashboard, name='student-dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    
    # Admin project management
    path('admin/projects/', views.admin_project_list_page, name='admin-project-list'),
    path('admin/projects/create/', views.admin_project_create_page, name='admin-project-create'),
    path('admin/projects/<int:pk>/edit/', views.admin_project_edit_page, name='admin-project-edit'),
    
    # Other pages - MAKE SURE ALL THESE EXIST
    path('topic-generator/', views.topic_generator_page, name='topic-generator-page'),
    path('about/', views.about_page, name='about-page'),
    path('terms/', views.terms_page, name='terms-page'),
    path('privacy/', views.privacy_page, name='privacy-page'),  # THIS WAS MISSING!
    path('contact/', views.contact_page, name='contact-page'),
    path('payment/confirm/', views.payment_confirm, name='payment-confirm'),
]