from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login with email or username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Allow authentication with either username or email
        if username is None:
            username = kwargs.get('email')
            
        if username is None:
            return None
            
        try:
            # Check if username is an email or username
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(email=username).order_by('id').first()
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None


