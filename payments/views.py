from django.conf import settings
from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import requests
import uuid

from projects.models import ProjectMaterial, Purchase

class InitPaymentView(views.APIView):
    """
    Initialize a Paystack transaction for purchasing a project.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
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

        # Create Pending Purchase
        Purchase.objects.create(
            user=request.user,
            project=project,
            amount=project.price,
            currency='NGN',
            paystack_reference=reference,
            status=Purchase.Status.PENDING
        )

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        data = {
            "email": email,
            "amount": amount_kobo,
            "reference": reference,
            "callback_url": f"{request.scheme}://{request.get_host()}/payments/confirm/",
            "metadata": {
                "project_id": project.id,
                "user_id": request.user.id
            }
        }

        try:
            resp = requests.post(f"{settings.PAYSTACK_BASE_URL}/transaction/initialize", json=data, headers=headers)
            resp_data = resp.json()

            if resp.status_code == 200 and resp_data['status']:
                return Response({
                    'authorization_url': resp_data['data']['authorization_url'],
                    'access_code': resp_data['data']['access_code'],
                    'reference': reference
                })
            else:
                return Response({'detail': 'Paystack initialization failed', 'error': resp_data}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': f'Payment error: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
