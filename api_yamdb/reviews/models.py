from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Administrator'),
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        max_length=20,
        default='user',
        blank=True
    )
    bio = models.TextField(
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
        max_length=255,
        null=True,
        blank=False,
    )

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )

    def __str__(self):
        return self.name


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.OneToOneField(
        'Review',
        on_delete=models.CASCADE,
        related_name='comment',
        null=True,
        blank=True
    )
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)


class Review(models.Model):
    title = models.ForeignKey(
        Title, related_name='reviews', on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User, related_name='reviews', on_delete=models.CASCADE
    )
    text = models.TextField()
    score = models.PositiveSmallIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('title', 'author') 

    def __str__(self):
        return f"Review by {self.author.username} on {self.title.name}"
