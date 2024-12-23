from api.serializers import (
    SingupSerializer,
    MeSerializer,
    UserSerializer,
    ReviewSerializer,
    TokenSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    CommentSerializer
)
from api.permissions import (
    UserAdmin,
    IsSuperUserOrAdmin,
    IsOwnerOrReadOnly,
    IsOwnerOrStaff
)
from reviews.models import (
    User,
    Category,
    Genre,
    Review,
    Title,
    Comment,
)

from django.forms import ValidationError
from django.db import IntegrityError
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, viewsets, status, permissions, generics, mixins
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination


@api_view(['POST'])
def singup(request):

    serializer = SingupSerializer(data=request.data)
    if serializer.is_valid():
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            from_email='',
            message=f'{confirmation_code}',
            recipient_list=[user.email]
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def token(request):

    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        if default_token_generator.check_token(
                user,
                serializer.validated_data['confirmation_code']
        ):
            token = RefreshToken.for_user(user)
            return Response(
                str(token.access_token),
                status=status.HTTP_200_OK
            )
        else:
            return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
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
        serializer_class=MeSerializer,
    )
    def get_edit_user(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id).order_by('-pub_date')

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = generics.get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class ReviewRetrievePatchDestroyView(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrStaff,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = (IsSuperUserOrAdmin,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(
            {"detail": "Метод не разрешен."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Метод не разрешен."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(
            {"detail": "Метод не разрешен."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Метод не разрешен."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().order_by('name')
    serializer_class = TitleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id).order_by('-pub_date')

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
