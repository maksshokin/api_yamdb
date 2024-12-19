from rest_framework import viewsets
from reviews.models import Review, Category, Genre, Title, User
from .serializers import ReviewSerializer, CategorySerializer, GenreSerializer, TitleSerializer, UserSerializer, NotAdminSerializer
from rest_framework.permissions import IsAdminUser, AllowAny
from api.permissions import IsSuperUserOrAdmin
from api_yamdb.settings import EMAIL
from django.shortcuts import get_object_or_404

from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        if title_id:
            return self.queryset.filter(title_id=title_id)
        return self.queryset
    
    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUserOrAdmin]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsSuperUserOrAdmin]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsSuperUserOrAdmin]


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me')
    def user_info(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = NotAdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class TokenViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    pass
