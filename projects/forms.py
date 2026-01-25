from django import forms
from django.utils.text import slugify
from .models import ProjectMaterial


class ProjectMaterialAdminForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True)
    abstract = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = ProjectMaterial
        fields = [
            'title', 'slug', 'description', 'abstract',
            'institution', 'department', 'course', 'category',
            'project_type', 'programming_language', 'framework',
            'database', 'keywords', 'price', 'status', 'document_file',
            'software_file', 'preview_images', 'is_featured'
        ]

    def clean_slug(self):
        slug = self.cleaned_data.get('slug') or ''
        title = self.cleaned_data.get('title') or ''
        if not slug:
            slug = slugify(title) if title else slugify(self.cleaned_data.get('description', ''))
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = self.clean_slug()
        if commit:
            instance.save()
        return instance