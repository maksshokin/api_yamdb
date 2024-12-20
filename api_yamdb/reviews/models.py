from django.db import models


class Title(models.Model):
    pass


class Category(models.Model):
    pass


class Genre(models.Model):
    pass


class User(models.Model):
    pass
    

class Review(models.Model):
    title = models.ForeignKey(Title, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    text = models.TextField()
    score = models.PositiveSmallIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('title', 'author') 

    def __str__(self):
        return f"Review by {self.author.username} on {self.title.name}"
