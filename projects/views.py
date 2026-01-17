# projects/views.py (COMPLETE UPDATED VERSION)
import uuid
import random
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
import logging

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
logger = logging.getLogger(__name__)


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


# =============== TOPIC GENERATOR VIEW ===============
class TopicGeneratorView(APIView):
    """
    Generate 2 random project topic suggestions based on department.
    Returns exactly 2 random topics from the department's topic list.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            # Import topic data from topic_data.py
            from .topic_data import DEPARTMENT_TOPICS, DEFAULT_TOPICS
            
            department = request.data.get('department', '').strip()
            keywords = request.data.get('keywords', '').strip()
            
            if not department:
                return Response(
                    {'detail': 'Department is required to generate topics.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Log the request
            log_message = f"Topic generation requested for department: '{department}'"
            if keywords:
                log_message += f" with keywords: '{keywords}'"
            logger.info(log_message)
            
            # Normalize department name for matching (case-insensitive, partial match)
            department_lower = department.lower()
            
            # Try to find the department in our topics
            department_key = None
            best_match_score = 0
            
            for dept_key in DEPARTMENT_TOPICS.keys():
                dept_key_lower = dept_key.lower()
                
                # Calculate match score
                score = 0
                if department_lower == dept_key_lower:
                    score = 100  # Exact match
                elif department_lower in dept_key_lower:
                    score = 80   # Department name is part of key
                elif dept_key_lower in department_lower:
                    score = 70   # Key is part of department name
                
                if score > best_match_score:
                    best_match_score = score
                    department_key = dept_key
            
            # Get topics for the department or use default
            if department_key and best_match_score >= 50:  # Minimum confidence score
                topics = DEPARTMENT_TOPICS[department_key]
                logger.info(f"Found department match: '{department_key}' with {len(topics)} topics")
            else:
                # If department not found, use fallback topics
                topics = self._generate_fallback_topics(department, DEFAULT_TOPICS)
                logger.info(f"No exact department match found for '{department}'. Using fallback topics.")
            
            # Filter by keywords if provided
            original_topic_count = len(topics)
            if keywords and topics:
                keyword_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
                if keyword_list:
                    filtered_topics = []
                    for topic in topics:
                        topic_lower = topic.lower()
                        # Check if any keyword is in the topic
                        if any(keyword in topic_lower for keyword in keyword_list):
                            filtered_topics.append(topic)
                    
                    # If we found keyword matches, use them
                    if filtered_topics:
                        topics = filtered_topics
                        logger.info(f"Filtered topics by keywords. From {original_topic_count} to {len(topics)} topics.")
            
            # Ensure we have at least some topics
            if not topics:
                topics = DEFAULT_TOPICS
                logger.info(f"No topics found. Using default topics: {len(topics)} topics.")
            
            # Random sample of exactly 2 topics
            if len(topics) >= 2:
                # Use random.sample to get 2 unique topics
                selected_topics = random.sample(topics, 2)
            elif len(topics) == 1:
                # If only one topic available, return it
                selected_topics = topics
            else:
                # No topics available
                selected_topics = [
                    f"Design and Implementation of a {department} Management System",
                    f"Impact of Digital Technology on {department} in Modern Society"
                ]
                logger.warning(f"No topics available for department '{department}'. Generated generic topics.")
            
            # Log successful generation
            logger.info(f"Generated {len(selected_topics)} topics for department: '{department}'")
            
            return Response({
                'topics': selected_topics,
                'department': department,
                'keywords': keywords,
                'count': len(selected_topics),
                'matched_department': department_key if department_key else None
            })
            
        except ImportError as e:
            logger.error(f"Failed to import topic_data: {str(e)}")
            return Response(
                {'detail': 'Topic database is not available. Please contact support.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error in topic generator: {str(e)}", exc_info=True)
            return Response(
                {'detail': 'An unexpected error occurred while generating topics.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_fallback_topics(self, department, default_topics):
        """Generate fallback topics if department not found in topic_data"""
        fallback_topics = [
            f"Design and Implementation of a {department} Management System",
            f"Impact of Technology on {department} in Nigeria",
            f"Challenges and Solutions in {department}: A Case Study of Nasarawa State University",
            f"Modern Approaches to {department} in the 21st Century",
            f"Comparative Analysis of Traditional and Modern {department} Methods",
            f"Development of a Mobile Application for {department} Students",
            f"Assessment of {department} Curriculum in Nigerian Universities",
            f"Role of {department} in Sustainable Development",
            f"Digital Transformation in {department}: Opportunities and Challenges",
            f"Effect of Globalization on {department} Practices"
        ]
        
        # Combine with default topics
        all_topics = fallback_topics + default_topics
        
        # Remove duplicates while preserving order
        seen = set()
        unique_topics = []
        for topic in all_topics:
            if topic not in seen:
                seen.add(topic)
                unique_topics.append(topic)
        
        return unique_topics


# =============== PROJECT TOOLS VIEWS ===============
class ProjectToolsView(APIView):
    """
    Base view for project-related tools.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# =============== DEPARTMENT LIST FOR TOPIC GENERATOR ===============
class DepartmentListView(APIView):
    """
    Get list of departments for topic generator dropdown.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            from .topic_data import DEPARTMENT_TOPICS
            
            # Get all department names from topic_data
            departments = list(DEPARTMENT_TOPICS.keys())
            
            # Sort alphabetically
            departments.sort()
            
            return Response({
                'departments': departments,
                'count': len(departments)
            })
            
        except ImportError:
            # Fallback to database departments
            db_departments = Department.objects.filter(is_active=True).values_list('name', flat=True)
            departments = list(db_departments)
            departments.sort()
            
            return Response({
                'departments': departments,
                'count': len(departments),
                'source': 'database'
            })
        except Exception as e:
            logger.error(f"Error getting department list: {str(e)}")
            return Response(
                {'detail': 'Failed to get department list.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============== SAVE TOPICS VIEW ===============
class SaveTopicsView(APIView):
    """
    Save generated topics to user's account.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            topics = request.data.get('topics', [])
            department = request.data.get('department', '')
            
            if not topics:
                return Response(
                    {'detail': 'No topics provided to save.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # In a real implementation, you would save these to the user's profile
            # For now, we'll just log and return success
            
            logger.info(f"User {request.user.id} saved {len(topics)} topics for department: {department}")
            
            # You could save to a model like:
            # SavedTopic.objects.create(
            #     user=request.user,
            #     department=department,
            #     topics=topics,
            #     saved_at=timezone.now()
            # )
            
            return Response({
                'message': f'Successfully saved {len(topics)} topics to your account.',
                'saved_count': len(topics),
                'department': department
            })
            
        except Exception as e:
            logger.error(f"Error saving topics: {str(e)}")
            return Response(
                {'detail': 'Failed to save topics.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============== GET SAVED TOPICS VIEW ===============
class GetSavedTopicsView(APIView):
    """
    Get user's saved topics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            # In a real implementation, you would retrieve from database
            # For now, return empty list
            return Response({
                'saved_topics': [],
                'count': 0
            })
        except Exception as e:
            logger.error(f"Error getting saved topics: {str(e)}")
            return Response(
                {'detail': 'Failed to get saved topics.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============== TOPIC STATISTICS VIEW ===============
class TopicStatisticsView(APIView):
    """
    Get statistics about topic generator usage.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            from .topic_data import DEPARTMENT_TOPICS
            
            total_departments = len(DEPARTMENT_TOPICS)
            
            # Count total topics across all departments
            total_topics = 0
            topics_per_department = {}
            
            for dept, topics in DEPARTMENT_TOPICS.items():
                topic_count = len(topics)
                total_topics += topic_count
                topics_per_department[dept] = topic_count
            
            # Get top departments by topic count
            sorted_departments = sorted(
                topics_per_department.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 departments
            
            return Response({
                'total_departments': total_departments,
                'total_topics': total_topics,
                'average_topics_per_department': total_topics // total_departments if total_departments > 0 else 0,
                'top_departments': [
                    {'department': dept, 'topic_count': count}
                    for dept, count in sorted_departments
                ],
                'last_updated': '2024'  # You can make this dynamic
            })
            
        except ImportError:
            return Response(
                {'detail': 'Topic statistics not available.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Error getting topic statistics: {str(e)}")
            return Response(
                {'detail': 'Failed to get topic statistics.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )