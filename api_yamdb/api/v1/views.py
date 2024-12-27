from django.contrib.auth.tokens import default_token_generator

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import CharFilter, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import (filters, generics, permissions, status,
                            viewsets)
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.permissions import IsOwnerOrStaff, IsSuperUserOrAdmin, UserAdmin
from api.v1.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SingupSerializer, TitleSerializer,
                             TokenSerializer, UserSerializer)
from reviews.models import Category, Genre, Review, Title, User


@api_view(['POST'])
def singup(request):

    serializer = SingupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def token(request):

    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )
    token = RefreshToken.for_user(user)
    return Response(
        str(token.access_token),
        status=status.HTTP_200_OK
    )


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserAdmin,)
    filter_backends = (filters.SearchFilter,)
    http_method_names = [
        'post',
        'get',
        'patch',
        'delete'
    ]
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False, url_path='me',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserSerializer,
    )
    def get_edit_user(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrStaff
    ]
    pagination_class = PageNumberPagination
    http_method_names = ['post', 'get', 'patch', 'delete']

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all().order_by('-pub_date')

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = generics.get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = (IsSuperUserOrAdmin,)
    filter_backends = [SearchFilter]
    search_fields = ['name', 'slug']
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(
            {"detail": "Метод не разрешен."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    filter_backends = [SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(
            {"detail": "Метод не разрешен."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class TitleFilter(FilterSet):
    genre = CharFilter(
        field_name="genre__slug",
        lookup_expr="iexact"
    )
    category = CharFilter(
        field_name="category__slug",
        lookup_expr="iexact"
    )
    name = CharFilter(
        field_name="name",
        lookup_expr="icontains"
    )
    year = NumberFilter(field_name="year")

    class Meta:
        model = Title
        fields = ["genre", "category", "name", "year"]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    serializer_class = TitleSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TitleFilter
    http_method_names = [
        'post',
        'get',
        'patch',
        'delete'
    ]


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrStaff
    ]
    pagination_class = PageNumberPagination
    http_method_names = ['post', 'get', 'patch', 'delete']

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        return review.comments.all().order_by('-pub_date')

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        serializer.save(author=self.request.user, review=review)
