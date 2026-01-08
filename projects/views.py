# projects/views.py (COMPLETE VERSION - includes everything)
import uuid
from datetime import timedelta
from pathlib import Path
from django.utils.text import slugify

import requests
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.db.models import Q, Sum, Count
from django.http import FileResponse, Http404
from rest_framework import permissions, status, generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from accounts.permissions import IsAdminUserRole
from django.contrib.auth import get_user_model
from .models import ProjectMaterial, Purchase, Download, Department, Category
from .serializers import (
    DepartmentSerializer,
    CategorySerializer,
    ProjectMaterialSerializer,
    PaymentInitSerializer,
    PaymentVerifySerializer,
    PurchaseSerializer,
    DownloadRequestSerializer,
    DownloadSerializer,
)

User = get_user_model()


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProjectMaterialViewSet(viewsets.ModelViewSet):
    queryset = ProjectMaterial.objects.filter(status=ProjectMaterial.Status.APPROVED)
    serializer_class = ProjectMaterialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by department
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        # Filter by project type
        project_type = self.request.query_params.get('project_type')
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(abstract__icontains=search) |
                Q(description__icontains=search) |
                Q(keywords__icontains=search)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering in ['title', '-title', 'year', '-year', 'price', '-price', 'download_count', '-download_count']:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    



# =============== PAYMENT VIEWS ===============
class PaymentInitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PaymentInitSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        project = serializer.validated_data['project']
        user = serializer.validated_data['user']

        if not settings.PAYSTACK_SECRET_KEY:
            return Response(
                {'detail': 'Paystack is not configured on the server.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Check if user already purchased this project
        existing_purchase = Purchase.objects.filter(
            user=user,
            project=project,
            status=Purchase.Status.PAID
        ).first()
        
        if existing_purchase:
            return Response(
                {'detail': 'You have already purchased this project.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Amount in kobo (Paystack expects smallest currency unit)
        amount_kobo = int(project.price * 100)
        
        # For free projects
        if amount_kobo == 0:
            purchase = Purchase.objects.create(
                user=user,
                project=project,
                amount=project.price,
                currency='NGN',
                paystack_reference=f"FREE-{uuid.uuid4().hex[:8]}",
                status=Purchase.Status.PAID,
                paid_at=timezone.now()
            )
            return Response(
                PurchaseSerializer(purchase).data,
                status=status.HTTP_200_OK
            )

        reference = str(uuid.uuid4())

        purchase = Purchase.objects.create(
            user=user,
            project=project,
            amount=project.price,
            currency='NGN',
            paystack_reference=reference,
            status=Purchase.Status.PENDING,
        )

        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        callback_url = request.build_absolute_uri("/payments/confirm/")
        data = {
            'email': user.email,
            'amount': amount_kobo,
            'reference': reference,
            'callback_url': callback_url,
            'metadata': {
                'purchase_id': purchase.id,
                'project_id': project.id,
                'user_id': user.id,
            },
        }

        try:
            resp = requests.post(
                f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
                json=data,
                headers=headers,
                timeout=30,
            )
            resp_data = resp.json()
        except Exception as e:
            purchase.status = Purchase.Status.FAILED
            purchase.save(update_fields=['status'])
            return Response(
                {'detail': f'Failed to initialize payment: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if resp.status_code != 200 or not resp_data.get('status'):
            purchase.status = Purchase.Status.FAILED
            purchase.save(update_fields=['status'])
            return Response(
                {
                    'detail': 'Failed to initialize payment with Paystack.',
                    'paystack_response': resp_data,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        auth_url = resp_data['data']['authorization_url']
        return Response(
            {
                'authorization_url': auth_url,
                'reference': reference,
                'purchase_id': purchase.id,
            },
            status=status.HTTP_200_OK,
        )


class PaymentVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference = serializer.validated_data['reference']

        try:
            purchase = Purchase.objects.get(paystack_reference=reference, user=request.user)
        except Purchase.DoesNotExist:
            return Response(
                {'detail': 'Purchase not found for this reference.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        try:
            resp = requests.get(
                f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}",
                headers=headers,
                timeout=30,
            )
            resp_data = resp.json()
        except Exception as e:
            return Response(
                {'detail': f'Failed to verify payment: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if resp.status_code != 200 or not resp_data.get('status'):
            return Response(
                {
                    'detail': 'Failed to verify payment with Paystack.',
                    'paystack_response': resp_data,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = resp_data['data']
        if data.get('status') == 'success':
            purchase.status = Purchase.Status.PAID
            purchase.paid_at = timezone.now()
            purchase.save(update_fields=['status', 'paid_at'])
        else:
            purchase.status = Purchase.Status.FAILED
            purchase.save(update_fields=['status'])

        return Response(PurchaseSerializer(purchase).data, status=status.HTTP_200_OK)


class StudentPurchaseListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user).select_related('project')


class StudentDownloadListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DownloadSerializer

    def get_queryset(self):
        return Download.objects.filter(user=self.request.user).select_related('project')


class AdminStatsOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get(self, request, *args, **kwargs):
        total_projects = ProjectMaterial.objects.count()
        pending_approvals = ProjectMaterial.objects.filter(status=ProjectMaterial.Status.PENDING).count()
        total_revenue = (
            Purchase.objects.filter(status=Purchase.Status.PAID)
            .aggregate(total=Sum('amount'))['total'] or 0
        )
        today = timezone.now().date()
        downloads_today = Download.objects.filter(downloaded_at__date=today).count()
        total_users = User.objects.count()

        return Response(
            {
                'total_projects': total_projects,
                'pending_approvals': pending_approvals,
                'total_revenue': float(total_revenue),
                'downloads_today': downloads_today,
                'total_users': total_users,
            },
            status=status.HTTP_200_OK,
        )


class DownloadRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = DownloadRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        project = serializer.validated_data['project']
        purchase = serializer.validated_data.get('purchase')
        user = serializer.validated_data['user']
        download_type = serializer.validated_data['download_type']

        # Validate download type based on project availability
        if download_type == 'software' and not project.software_file:
            return Response(
                {'detail': 'Software file is not available for this project.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a download record with short-lived token
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(minutes=30)

        download = Download.objects.create(
            user=user,
            project=project,
            purchase=purchase,
            token=token,
            expires_at=expires_at,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            download_type=download_type,
        )

        # Increment project download count
        project.download_count = (project.download_count or 0) + 1
        project.save(update_fields=['download_count'])

        download_url = request.build_absolute_uri(f"/api/downloads/file/{token}/")

        return Response(
            {
                'download_url': download_url,
                'expires_at': expires_at,
                'token': token,
            },
            status=status.HTTP_200_OK,
        )


class DownloadFileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, token, *args, **kwargs):
        try:
            download = Download.objects.select_related('project').get(token=token)
        except Download.DoesNotExist:
            return Response({'detail': 'Invalid or expired download link.'}, status=status.HTTP_404_NOT_FOUND)

        if download.user != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)

        if not download.expires_at or download.expires_at < timezone.now():
            return Response({'detail': 'Download link has expired.'}, status=status.HTTP_410_GONE)

        project = download.project
        
        # Get the appropriate file based on download type
        if download.download_type == 'document':
            file_field = project.document_file
        elif download.download_type == 'software':
            file_field = project.software_file
        else:
            # For 'both', return document first
            file_field = project.document_file

        if not file_field:
            raise Http404("File not found")

        try:
            file_path = file_field.path
            if not Path(file_path).exists():
                raise Http404("File not found on server")
        except ValueError:
            # If file is stored in S3 or similar, use url
            file_path = file_field.name

        response = FileResponse(open(file_field.path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{Path(file_field.name).name}"'
        
        return response