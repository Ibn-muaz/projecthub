from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = 'STUDENT', _('Student')
        ADMIN = 'ADMIN', _('Admin')
        SUPER_ADMIN = 'SUPER_ADMIN', _('Super Admin')

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT,
    )
    institution = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    def is_email_verified(self) -> bool:
        return self.email_verified_at is not None

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.email})"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='email_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])

    def is_valid(self) -> bool:
        return self.used_at is None
