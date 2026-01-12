from django import forms
from django.utils.text import slugify
from .models import ProjectMaterial


class ProjectMaterialAdminForm(forms.ModelForm):

    class Meta:
        model = ProjectMaterial
        fields = [
            'title', 'slug', 'abstract', 'description', 'year',
            'institution', 'department', 'course', 'category',
            'project_type', 'programming_language', 'framework',
            'database', 'keywords', 'price', 'status', 'document_file',
            'software_file', 'preview_images', 'is_featured'
        ]

    def clean_slug(self):
        slug = self.cleaned_data.get('slug') or ''
        title = self.cleaned_data.get('title') or ''
        if not slug:
            slug = slugify(title)
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = self.clean_slug()
        if commit:
            instance.save()
        return instance