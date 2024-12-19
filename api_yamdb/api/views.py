from rest_framework import viewsets
from reviews.models import Review, Category, Genre, Title
from .serializers import ReviewSerializer, CategorySerializer, GenreSerializer, TitleSerializer
from rest_framework.permissions import IsAdminUser


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        if title_id:
            return self.queryset.filter(title_id=title_id)
        return self.queryset


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminUser]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdminUser]
