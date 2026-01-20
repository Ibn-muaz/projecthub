from django.conf import settings
from django.urls import reverse
from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import requests
import uuid
import logging

from projects.models import ProjectMaterial, Purchase

# Add logger
logger = logging.getLogger(__name__)

class InitPaymentView(views.APIView):
    """
    Initialize a Paystack transaction for purchasing a project.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            project_id = request.data.get('project_id')
            if not project_id:
                return Response({'detail': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            project = get_object_or_404(ProjectMaterial, pk=project_id)
            
            # Check if already purchased
            if Purchase.objects.filter(user=request.user, project=project, status=Purchase.Status.PAID).exists():
                return Response({'detail': 'You have already purchased this project'}, status=status.HTTP_400_BAD_REQUEST)

            email = request.user.email
            amount_kobo = int(project.price * 100)  # Paystack expects kobo
            reference = f"PH-{uuid.uuid4().hex[:12]}"

            # Log payment attempt
            logger.info(f"Payment initialization attempt for project {project_id} by user {request.user.id}")

            # Create Pending Purchase
            purchase = Purchase.objects.create(
                user=request.user,
                project=project,
                amount=project.price,
                currency='NGN',
                paystack_reference=reference,
                status=Purchase.Status.PENDING
            )

            # Verify Paystack settings are configured
            if not settings.PAYSTACK_SECRET_KEY or settings.PAYSTACK_SECRET_KEY.strip() == '':
                logger.error("PAYSTACK_SECRET_KEY is not configured or is empty")
                purchase.status = Purchase.Status.FAILED
                purchase.save()
                return Response({
                    'detail': 'Payment service is not configured properly. Please contact support.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            if not settings.PAYSTACK_BASE_URL or settings.PAYSTACK_BASE_URL.strip() == '':
                logger.error("PAYSTACK_BASE_URL is not configured")
                purchase.status = Purchase.Status.FAILED
                purchase.save()
                return Response({
                    'detail': 'Payment service is not configured properly'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }
            
            # Construct callback URL using Django reverse to ensure correct path
            try:
                callback_url = request.build_absolute_uri(reverse('payment-confirm'))
            except Exception as e:
                logger.warning(f"Could not construct callback URL via reverse: {str(e)}")
                if getattr(settings, 'PAYSTACK_CALLBACK_URL', None):
                    callback_url = settings.PAYSTACK_CALLBACK_URL
                else:
                    scheme = request.scheme or 'https'
                    host = request.get_host() or request.META.get('HTTP_HOST', 'localhost')
                    # Fallback to core app path
                    callback_url = f"{scheme}://{host}/payment/confirm/"
            
            data = {
                "email": email,
                "amount": amount_kobo,
                "reference": reference,
                "callback_url": callback_url,
                "metadata": {
                    "project_id": project.id,
                    "user_id": request.user.id,
                    "purchase_id": purchase.id
                }
            }

            # Add timeout to prevent hanging (Paystack typically responds quickly)
            timeout = 30  # seconds
            paystack_url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
            
            logger.debug(f"Calling Paystack URL: {paystack_url}")
            logger.debug(f"Request data: {data}")
            
            resp = requests.post(
                paystack_url, 
                json=data, 
                headers=headers, 
                timeout=timeout,
                verify=True  # SSL verification
            )
            
            logger.info(f"Paystack response status: {resp.status_code}")
            logger.debug(f"Paystack response: {resp.text}")
            
            resp_data = resp.json()

            if resp.status_code == 200 and resp_data.get('status'):
                return Response({
                    'authorization_url': resp_data['data']['authorization_url'],
                    'access_code': resp_data['data']['access_code'],
                    'reference': reference
                })
            else:
                # Update purchase status to failed
                purchase.status = Purchase.Status.FAILED
                purchase.save()
                
                error_message = resp_data.get('message', 'Unknown Paystack error')
                logger.error(f"Paystack initialization failed: {error_message}")
                logger.error(f"Full Paystack response: {resp_data}")
                
                return Response({
                    'detail': f'Payment initialization failed: {error_message}',
                    'paystack_error': resp_data
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.exceptions.Timeout:
            logger.error(f"Paystack request timed out after {timeout} seconds")
            purchase.status = Purchase.Status.FAILED
            purchase.save()
            return Response({
                'detail': 'Payment service is taking too long to respond. Please try again.'
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Paystack: {str(e)}")
            purchase.status = Purchase.Status.FAILED
            purchase.save()
            return Response({
                'detail': 'Cannot connect to payment service. Please check your internet connection.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception with Paystack: {str(e)}")
            purchase.status = Purchase.Status.FAILED
            purchase.save()
            return Response({
                'detail': f'Payment service error: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except Exception as e:
            logger.exception(f"Unexpected error in payment initialization: {str(e)}")
            # Only update purchase status if it was created
            if 'purchase' in locals():
                purchase.status = Purchase.Status.FAILED
                purchase.save()
            return Response({
                'detail': 'An unexpected error occurred. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
