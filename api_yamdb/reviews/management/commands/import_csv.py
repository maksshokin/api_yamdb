import csv
import os

from django.core.management.base import BaseCommand

from reviews.constants import (CATEGORY_CSV, COMMENTS_CSV, CSV_FILES_PATH,
                               GENRE_CSV, GENRE_TITLE_CSV, REVIEW_CSV,
                               TITLES_CSV, USERS_CSV)
from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):
    help = 'Import data from csv files'

    def handle(self, *args, **kwargs):
        with open(
            os.path.join(CSV_FILES_PATH, USERS_CSV), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                User.objects.get_or_create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                )

        with open(
            os.path.join(CSV_FILES_PATH, CATEGORY_CSV), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                Category.objects.get_or_create(
                    name=row['name'],
                    slug=row['slug'],
                )

        with open(
            os.path.join(CSV_FILES_PATH, GENRE_CSV), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                Genre.objects.get_or_create(
                    name=row['name'],
                    slug=row['slug'],
                )

        with open(
            os.path.join(CSV_FILES_PATH, TITLES_CSV), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = Category.objects.get(id=row['category'])
                Title.objects.get_or_create(
                    name=row['name'],
                    year=row['year'],
                    category=category,
                )

        with open(
            os.path.join(CSV_FILES_PATH, GENRE_TITLE_CSV), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)

        with open(
            os.path.join(CSV_FILES_PATH, REVIEW_CSV), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                author = User.objects.get(id=row['author'])
                Review.objects.get_or_create(
                    id=row['id'],
                    title=title,
                    text=row['text'],
                    author=author,
                    score=row['score'],
                    pub_date=row['pub_date'],
                )

        with open(
            os.path.join(CSV_FILES_PATH, COMMENTS_CSV), encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                review = Review.objects.get(id=row['review_id'])
                author = User.objects.get(id=row['author'])
                Comment.objects.get_or_create(
                    id=row['id'],
                    review=review,
                    text=row['text'],
                    author=author,
                    pub_date=row['pub_date'],
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully imported')
        )
