# accounts/views.py
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer
# Remove or comment out EmailVerificationToken if it doesn't exist
# from .models import EmailVerificationToken

User = get_user_model()


# API Views
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# Comment out VerifyEmailView if EmailVerificationToken doesn't exist
"""
class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        token_str = request.query_params.get('token')
        if not token_str:
            return Response({'detail': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = EmailVerificationToken.objects.select_related('user').get(token=token_str)
        except EmailVerificationToken.DoesNotExist:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        if not token.is_valid():
            return Response({'detail': 'Token already used.'}, status=status.HTTP_400_BAD_REQUEST)

        user = token.user
        user.email_verified_at = user.email_verified_at or token.created_at
        user.save(update_fields=['email_verified_at'])
        token.mark_used()
        return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)
"""


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {'detail': 'Invalid or expired refresh token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# Web Views (for session-based authentication)
def web_register_view(request):
    """Handle web registration"""
    if request.user.is_authenticated:
        return redirect('landing')
    
    if request.method == 'POST':
        from django.contrib.auth.forms import UserCreationForm
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login after registration
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('landing')
        else:
            # Pass errors to template
            return render(request, 'core/register.html', {'form': form})
    else:
        form = UserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})


@login_required
def web_profile_view(request):
    """Web profile view"""
    return render(request, 'core/profile.html', {'user': request.user})