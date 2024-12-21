from django.contrib.auth import get_user_model
from django.db import models

from django.core.validators import RegexValidator

User = get_user_model() 


class BaseModel(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(regex=r'^[-a-zA-Z0-9_]+$', message='Invalid slug format')]
    )

    def __str__(self):
        return self.name

 
class Category(BaseModel):
    pass


class Genre(BaseModel):
    pass


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
