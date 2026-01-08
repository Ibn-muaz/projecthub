# projects/models.py
import os
import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Department(models.Model):
    """Department/Course model"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    faculty = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """Project category model"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class ProjectMaterial(models.Model):
    """Project material model"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        FEATURED = 'featured', 'Featured'
    
    class ProjectType(models.TextChoices):
        DOCUMENTATION = 'documentation', 'Documentation Only'
        SOFTWARE = 'software', 'Software Project'
        BOTH = 'both', 'Documentation + Software'
    
    # Basic Information
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    abstract = models.TextField()
    description = models.TextField(blank=True)
    
    # Academic Information
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='projects')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    institution = models.CharField(max_length=200, default="Not Specified")
    course = models.CharField(max_length=200, blank=True)
    year = models.IntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    
    # Project Type
    project_type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        default=ProjectType.DOCUMENTATION
    )
    
    # Technical Details
    programming_language = models.CharField(max_length=100, blank=True)
    framework = models.CharField(max_length=100, blank=True)
    database = models.CharField(max_length=100, blank=True)
    keywords = models.TextField(help_text="Comma-separated keywords", blank=True)
    
    # Files
    def project_file_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{slugify(instance.title)}-{uuid.uuid4().hex[:8]}.{ext}"
        return f'projects/documents/{filename}'
    
    def software_file_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{slugify(instance.title)}-software-{uuid.uuid4().hex[:8]}.{ext}"
        return f'projects/software/{filename}'
    
    document_file = models.FileField(
        upload_to=project_file_path,
        verbose_name="Project Document (PDF/DOC)"
    )
    software_file = models.FileField(
        upload_to=software_file_path,
        blank=True,
        null=True,
        verbose_name="Software/Source Code (ZIP)"
    )
    preview_images = models.ImageField(
        upload_to='projects/previews/',
        blank=True,
        null=True,
        help_text="Preview/screenshot of the project"
    )
    
    # Pricing and Status
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    is_featured = models.BooleanField(default=False)
    
    # Metrics
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Document Metadata
    page_count = models.IntegerField(null=True, blank=True, help_text="Number of pages in the document")
    file_format = models.CharField(max_length=50, null=True, blank=True, help_text="File format (e.g. PDF, DOCX)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval and Creator fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_projects',
        null=True,
        blank=True
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_projects'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def has_software(self):
        return bool(self.software_file)
    
    def get_keywords_list(self):
        if self.keywords:
            return [k.strip() for k in self.keywords.split(',')]
        return []
    
    def increment_download_count(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])


class Purchase(models.Model):
    """Purchase model for tracking project purchases"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    project = models.ForeignKey(ProjectMaterial, on_delete=models.CASCADE, related_name='purchases')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='NGN')
    paystack_reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.project} - {self.amount}"





class Download(models.Model):
    """Download tracking model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads')
    project = models.ForeignKey(ProjectMaterial, on_delete=models.CASCADE, related_name='downloads')
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, null=True, blank=True, related_name='downloads')
    token = models.CharField(max_length=100, unique=True, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    download_type = models.CharField(
        max_length=20,
        choices=[('document', 'Document Only'), ('software', 'Software Only'), ('both', 'Both')]
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f"{self.user} downloaded {self.project}"