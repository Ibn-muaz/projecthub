from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from accounts import views as accounts_views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('projects/', views.project_list, name='project-list-page'),
    path('projects/<slug:slug>/', views.project_detail, name='project-detail-page'),

    path('dashboard/', views.student_dashboard, name='student-dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/projects/', views.admin_project_list_page, name='admin-projects-page'),
    path('admin/projects/new/', views.admin_project_create_page, name='admin-projects-create'),
    path('admin/projects/<int:pk>/edit/', views.admin_project_edit_page, name='admin-projects-edit'),

    path('payments/confirm/', views.payment_confirm, name='payment-confirm'),
    path('tools/topic-generator/', views.topic_generator_page, name='topic-generator-page'),

    path('about/', views.about_page, name='about-page'),
    path('terms/', views.terms_page, name='terms-page'),
    path('privacy/', views.privacy_page, name='privacy-page'),
    path('contact/', views.contact_page, name='contact-page'),

    # Auth URLs
    path('login/', views.login_page, name='login-page'),
    path('register/', views.register_page, name='register-page'),
    path('logout/', LogoutView.as_view(next_page='landing'), name='logout-page'),
]