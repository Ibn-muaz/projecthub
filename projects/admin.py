# projects/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Department, Category, ProjectMaterial, Purchase, Download
from .forms import ProjectMaterialAdminForm


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'faculty', 'is_active']
    list_filter = ['is_active', 'faculty']
    search_fields = ['name', 'code', 'faculty']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(ProjectMaterial)
class ProjectMaterialAdmin(admin.ModelAdmin):
    form = ProjectMaterialAdminForm
    list_display = ['title', 'department', 'status', 'price', 'download_count', 'created_at']
    list_filter = ['status', 'department', 'category', 'project_type', 'year']
    search_fields = ['title', 'abstract', 'description', 'keywords']
    readonly_fields = ['download_count', 'view_count', 'slug', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'abstract', 'description')
        }),
        ('Academic Information', {
            'fields': ('department', 'category', 'institution', 'course', 'year')
        }),
        ('Technical Details', {
            'fields': ('project_type', 'programming_language', 'framework', 'database', 'keywords')
        }),
        ('Files', {
            'fields': ('document_file', 'software_file', 'preview_images')
        }),
        ('Pricing and Status', {
            'fields': ('price', 'status', 'is_featured')
        }),
        ('Metrics', {
            'fields': ('download_count', 'view_count')
        }),
        ('Metadata', {
            'fields': ('created_by', 'approved_by', 'approved_at', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'document_file' in form.changed_data and obj.document_file:
            try:
                from PyPDF4 import PdfFileReader
                from io import BytesIO

                # Reset the file pointer to the beginning
                obj.document_file.seek(0)
                
                # Read the file content into a BytesIO object
                file_content = BytesIO(obj.document_file.read())
                
                # Create a PDF reader object
                pdf_reader = PdfFileReader(file_content, strict=False)
                
                # Get the number of pages
                obj.page_count = pdf_reader.getNumPages()
                
                # Reset the file pointer again before saving
                obj.document_file.seek(0)
            except Exception as e:
                # Handle cases where the file is not a valid PDF or other errors
                print(f"Error processing PDF file: {e}")
                obj.page_count = None

        if not change:  # If creating a new project (not editing)
            obj.status = ProjectMaterial.Status.APPROVED
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
            if not obj.created_by:  # If created_by is not set
                obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'project', 'amount', 'status', 'paid_at', 'created_at']
    list_filter = ['status', 'currency']
    search_fields = ['user__email', 'project__title', 'paystack_reference']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'download_type', 'downloaded_at']
    list_filter = ['download_type']
    search_fields = ['user__email', 'project__title', 'token']
    readonly_fields = ['downloaded_at']