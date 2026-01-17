from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class Users(AbstractUser):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    ROLE_CHOICES = [
        ('STUDENT', 'STUDENT'),
        ('INSTRUCTOR', 'INSTRUCTOR'),
        ('TPO', 'TPO'),
        ('INTERVIEWER', 'INTERVIEWER'),
        ('ADMIN', 'ADMIN')
    ]

    username = models.CharField(max_length=150, unique=False, null=False, blank=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=25, choices=ROLE_CHOICES)
    phone_no = models.PositiveBigIntegerField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role', 'password']

    def __str__(self):
        return f"{self.email} → {self.role}"
