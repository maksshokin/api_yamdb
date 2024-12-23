from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

from reviews.validators import validate_username


ROLES = (
    ('user', 'user'),
    ('moderator', 'moderator'),
    ('admin', 'admin'),
)

class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=(validate_username,)
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default='user',
        blank=True,
    )
    bio = models.TextField(
        blank=True,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
    )
    confirmation_code = models.CharField(
        max_length=255,
        null=True,
        blank=False,
    )

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return self.username
    
    class Meta:
        ordering = ('id',)


class BaseModel(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Invalid slug format'
            )
        ]
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Category(BaseModel):
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class Genre(BaseModel):
    
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0, message="Год не может быть отрицательным.")
        ]
    )
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ['name']

    def __str__(self):
        return self.name


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


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
