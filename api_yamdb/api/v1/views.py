from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.filters import TitleFilter
from api.v1.permissions import IsOwnerOrStaff, IsSuperUserOrAdmin, UserAdmin
from api.v1.serializers import (CategorySerializer, CommentSerializer,
                                GenreSerializer, ReviewSerializer,
                                SingupSerializer, TitleReadSerializer,
                                TitlePostSerializer, TokenSerializer,
                                UserSerializer)
from reviews.models import Category, Genre, Review, Title, User


class BaseCategoryGenreViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin
):
    permission_classes = (IsSuperUserOrAdmin,)
    filter_backends = [SearchFilter]
    lookup_field = 'slug'

    def get_serializer_class(self):
        model = self.queryset.model
        if model == Category:
            return CategorySerializer
        elif model == Genre:
            return GenreSerializer
        return super().get_serializer_class()


class BaseCommentReviewViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    http_method_names = ['post', 'get', 'patch', 'delete']
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrStaff
    ]

    def get_review_or_title(self, model, **kwargs):
        return get_object_or_404(model, **kwargs)

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return self.get_review_or_title(
            Review,
            id=review_id,
            title_id=title_id
        )


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


class ReviewViewSet(BaseCommentReviewViewSet):
    serializer_class = ReviewSerializer

    def get_title(self):
        return self.get_review_or_title(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all().order_by('-pub_date')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CategoryViewSet(BaseCategoryGenreViewSet):
    queryset = Category.objects.all().order_by('name')
    search_fields = ['name', 'slug']


class GenreViewSet(BaseCategoryGenreViewSet):
    queryset = Genre.objects.all().order_by('name')
    search_fields = ['name']


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (IsSuperUserOrAdmin,)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TitleFilter
    http_method_names = [
        'post',
        'get',
        'patch',
        'delete'
    ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitlePostSerializer


class CommentViewSet(BaseCommentReviewViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return self.get_review().comments.all().order_by('-pub_date')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
