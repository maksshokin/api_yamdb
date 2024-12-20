from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField(
         max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        max_length=150,
        default='user',
        blank=True
    )
    bio = models.TextField(
        max_length=250,
        blank=True,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=150,
        null=True,
        blank=False,
    )

    def __str__(self):
        return self.username
