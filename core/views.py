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
    return render(request, 'core/landing.html', {
        'featured_projects': featured_projects,
        'faculty_departments': FACULTY_DEPARTMENTS,
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


def admin_dashboard(request):
    # Stats are loaded via JS from /api/admin/stats/overview/
    return render(request, 'core/admin_dashboard.html')


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
    return render(request, 'core/topic_generator.html', {
        'departments': NSUK_DEPARTMENTS,
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
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('landing')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'landing')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
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