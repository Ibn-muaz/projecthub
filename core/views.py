from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate
from django.contrib import messages

from accounts.forms import UserRegistrationForm

from projects.models import ProjectMaterial
from projects.constants import NSUK_DEPARTMENTS, FACULTY_DEPARTMENTS
from projects.forms import ProjectMaterialAdminForm


def landing_page(request):
    featured_projects = ProjectMaterial.objects.filter(
        status=ProjectMaterial.Status.APPROVED
    ).order_by('-download_count')[:6]
    
    # Group departments by faculty from DB
    from projects.models import Department
    
    # specialized logic to grouping active departments by faculty
    departments = Department.objects.filter(is_active=True).order_by('faculty', 'name')
    faculty_map = {}
    for dept in departments:
        fac = dept.faculty or "Other"
        if fac not in faculty_map:
            faculty_map[fac] = []
        faculty_map[fac].append(dept.name)
        
    return render(request, 'core/landing.html', {
        'featured_projects': featured_projects,
        'faculty_departments': faculty_map,
    })


def project_list(request):
    qs = ProjectMaterial.objects.filter(status=ProjectMaterial.Status.APPROVED)

    q = request.GET.get('q')
    department = request.GET.get('department')
    course = request.GET.get('course')
    institution = request.GET.get('institution')
    year = request.GET.get('year')
    project_type = request.GET.get('project_type')

    if q:
        qs = qs.filter(title__icontains=q)
    if department:
        qs = qs.filter(department__name__iexact=department)
    if course:
        qs = qs.filter(course__iexact=course)
    if institution:
        qs = qs.filter(institution__iexact=institution)
    if year:
        qs = qs.filter(year=year)
    if project_type:
        qs = qs.filter(project_type=project_type)

    return render(request, 'core/project_list.html', {
        'projects': qs,
    })


def project_detail(request, slug):
    project = get_object_or_404(
        ProjectMaterial,
        slug=slug,
        status=ProjectMaterial.Status.APPROVED,
    )
    return render(request, 'core/project_detail.html', {
        'project': project,
    })


def student_dashboard(request):
    # Data is loaded via JS from /api/me/purchases and /api/me/downloads
    return render(request, 'core/student_dashboard.html')


@login_required
def admin_dashboard(request):
    """Admin dashboard with stats and pending projects"""
    if not _require_admin(request):
        return HttpResponseForbidden("Not allowed")
    
    from projects.models import ProjectMaterial, Purchase, Download, Department
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta
    
    # Get stats
    total_projects = ProjectMaterial.objects.count()
    pending_projects = ProjectMaterial.objects.filter(status=ProjectMaterial.Status.PENDING).count()
    pending_projects_list = ProjectMaterial.objects.filter(status=ProjectMaterial.Status.PENDING).order_by('-created_at')[:5]
    
    # Revenue from paid purchases
    total_revenue = Purchase.objects.filter(status=Purchase.Status.PAID).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Downloads today
    today = timezone.now().date()
    downloads_today = Download.objects.filter(downloaded_at__date=today).count()
    
    # Active users (users who logged in within last 30 days)
    from accounts.models import User
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()
    
    # Storage (placeholder)
    storage_used = 0.5  # GB placeholder
    
    return render(request, 'core/admin_dashboard.html', {
        'total_projects': total_projects,
        'pending_projects': pending_projects,
        'pending_projects_list': pending_projects_list,
        'total_revenue': total_revenue,
        'downloads_today': downloads_today,
        'active_users': active_users,
        'storage_used': storage_used,
        'recent_activity': [],  # Placeholder for activity feed
    })


def _require_admin(request):
    if not request.user.is_authenticated:
        return False
    return getattr(request.user, 'role', None) in ('ADMIN', 'SUPER_ADMIN')


@login_required
def admin_project_list_page(request):
    if not _require_admin(request):
        return HttpResponseForbidden("Not allowed")
    qs = ProjectMaterial.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_project_list.html', {
        'page_obj': page_obj,
    })


@login_required
def admin_project_create_page(request):
    if not _require_admin(request):
        return HttpResponseForbidden("Not allowed")
    if request.method == 'POST':
        form = ProjectMaterialAdminForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'core/admin_project_form.html', {
                'form': ProjectMaterialAdminForm(),
                'success': True,
            })
    else:
        form = ProjectMaterialAdminForm()
    return render(request, 'core/admin_project_form.html', {
        'form': form,
    })


@login_required
def admin_project_edit_page(request, pk):
    if not _require_admin(request):
        return HttpResponseForbidden("Not allowed")
    project = get_object_or_404(ProjectMaterial, pk=pk)
    if request.method == 'POST':
        form = ProjectMaterialAdminForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return render(request, 'core/admin_project_form.html', {
                'form': form,
                'success': True,
                'project': project,
            })
    else:
        form = ProjectMaterialAdminForm(instance=project)
    return render(request, 'core/admin_project_form.html', {
        'form': form,
        'project': project,
    })


def payment_confirm(request):
    # Paystack will redirect here after payment with ?reference=&project_id=
    return render(request, 'core/payment_confirm.html')


def topic_generator_page(request):
    from projects.models import Department
    # Fetch all active departments from DB
    departments = Department.objects.filter(is_active=True).values_list('name', flat=True).order_by('name')
    
    return render(request, 'core/topic_generator.html', {
        'departments': departments,
    })


def about_page(request):
    return render(request, 'core/about.html')


def terms_page(request):
    return render(request, 'core/terms.html')


def privacy_page(request):
    return render(request, 'core/privacy.html')


def contact_page(request):
    return render(request, 'core/contact.html')


# ADD THESE TWO FUNCTIONS - THEY WERE MISSING
def login_page(request):
    """Handle user login with email"""
    if request.user.is_authenticated:
        return redirect('landing')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate using the custom backend (email or username)
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'landing')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'core/login.html')


def register_page(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('landing')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login after registration
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('landing')
        else:
            # If form is invalid, pass errors to template
            return render(request, 'core/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})