from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveBigIntegerField()
    description = models.TextField(null=True, blank=True)

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
    text = models.TextField()
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )



