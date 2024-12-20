from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField(
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        default='user',
        blank=True
    )
    bio = models.TextField(
        blank=True,
    )
    first_name = models.CharField(
        blank=True
    )
    last_name = models.CharField(
        blank=True
    )
    confirmation_code = models.CharField(
        null=True,
        blank=False,
    )

    def __str__(self):
        return self.username
