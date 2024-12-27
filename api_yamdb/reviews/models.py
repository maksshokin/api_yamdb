from api.constants import (CORE_NAME_MAX_LENGTH, MAX_SCORE, MIN_SCORE,
                           EMAIL_MAX_LENGTH,
                           CORE_SLUG_MAX_LENGTH, ROLE_MAX_LENGTH,
                           TITLE_NAME_MAX_LENGTH, USERNAME_MAX_LENGTH)
from django.contrib.auth.models import AbstractUser
from django.db import models
from reviews.validators import ValidateUsername, ValidateYear
from django.db.models import UniqueConstraint
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser, ValidateUsername):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        validators=[ValidateUsername()],
        max_length=USERNAME_MAX_LENGTH,
        unique=True
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=ROLE_MAX_LENGTH,
        choices=ROLES, default=USER
    )
    bio = models.TextField(
        verbose_name='Биография',
        null=True,
        blank=True
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class CoreModel(models.Model):
    name = models.CharField(
        max_length=CORE_NAME_MAX_LENGTH, verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=CORE_SLUG_MAX_LENGTH, unique=True, verbose_name='URL'
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(CoreModel):

    class Meta(CoreModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CoreModel):

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название произведения',
        max_length=TITLE_NAME_MAX_LENGTH)
    year = models.SmallIntegerField(
        verbose_name='Год',
        validators=[ValidateYear()],
    )
    description = models.TextField(
        verbose_name='Описание произведения', blank=True, null=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        related_name='reviews',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='reviews',
        on_delete=models.CASCADE
    )
    text = models.TextField(verbose_name='Текст')
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(
                MIN_SCORE,
                message='Оценка должна быть не меньше 1.'
            ),
            MaxValueValidator(
                MAX_SCORE,
                message='Оценка должна быть не больше 10.'
            )
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            UniqueConstraint(fields=['title', 'author'], name='unique_review')
        ]
        ordering = ['-pub_date']

    def __str__(self):
        return f"Review by {self.author.username} on {self.title.name}"


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    text = models.TextField(verbose_name=u'Текст комментария')
    pub_date = models.DateTimeField(
        verbose_name=u'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.review.title.name}"
