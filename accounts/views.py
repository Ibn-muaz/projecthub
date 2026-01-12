# accounts/views.py
from django.shortcuts import redirect
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate
from django.contrib import messages

from .forms import UserRegistrationForm
from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()


# ============ API VIEWS ============
class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """API endpoint for user logout"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """API endpoint to get current user info"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# ============ WEB VIEWS (for accounts app) ============
def web_register_view(request):
    """Web registration view (redirects to core app)"""
    return redirect('register-page')


def web_profile_view(request):
    """Web profile page"""
    if not request.user.is_authenticated:
        return redirect('login-page')
    return redirect('student-dashboard')  # Redirect to dashboard for now