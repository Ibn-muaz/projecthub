# projects/serializers.py
from rest_framework import serializers
from .models import ProjectMaterial, Purchase, Download, Department, Category


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'faculty', 'description', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'is_active']


class ProjectMaterialSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ProjectMaterial
        fields = [
            'id', 'title', 'slug', 'abstract', 'description',
            'department', 'department_name', 'category', 'category_name',
            'institution', 'course', 'year', 'project_type',
            'programming_language', 'framework', 'database', 'keywords',
            'price', 'status', 'is_featured', 'download_count', 'view_count',
            'created_by', 'created_by_name', 'approved_by', 'approved_at',
            'created_at', 'updated_at', 'average_rating', 'rating_count'
        ]
        read_only_fields = [
            'slug', 'download_count', 'view_count', 'created_by',
            'approved_by', 'approved_at', 'created_at', 'updated_at'
        ]





class PaymentInitSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        if not user or not user.is_authenticated:
            raise serializers.ValidationError('Authentication required.')

        project_id = attrs['project_id']
        try:
            project = ProjectMaterial.objects.get(id=project_id)
        except ProjectMaterial.DoesNotExist:
            raise serializers.ValidationError('Project not found.')

        if project.status != ProjectMaterial.Status.APPROVED:
            raise serializers.ValidationError('Project is not available for purchase.')

        attrs['project'] = project
        attrs['user'] = user
        return attrs


class PurchaseSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'project', 'project_title', 'user', 'user_email',
            'amount', 'currency', 'paystack_reference', 'status',
            'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class PaymentVerifySerializer(serializers.Serializer):
    reference = serializers.CharField()


class DownloadRequestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    download_type = serializers.ChoiceField(
        choices=[('document', 'Document Only'), ('software', 'Software Only'), ('both', 'Both')],
        default='document'
    )

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        if not user or not user.is_authenticated:
            raise serializers.ValidationError('Authentication required.')

        project_id = attrs['project_id']
        try:
            project = ProjectMaterial.objects.get(id=project_id)
        except ProjectMaterial.DoesNotExist:
            raise serializers.ValidationError('Project not found.')

        # Ensure user has a successful purchase
        purchase = (
            Purchase.objects.filter(
                user=user,
                project=project,
                status=Purchase.Status.PAID,
            )
            .order_by('-created_at')
            .first()
        )
        if not purchase:
            raise serializers.ValidationError('No valid purchase found for this project.')

        # Check if it's a free project
        if project.price == 0:
            attrs['purchase'] = None
        else:
            attrs['purchase'] = purchase
        
        attrs['project'] = project
        attrs['user'] = user
        return attrs


class DownloadSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = Download
        fields = [
            'id', 'project', 'project_title', 'purchase',
            'token', 'download_type', 'ip_address', 'user_agent',
            'downloaded_at', 'expires_at'
        ]
        read_only_fields = fields