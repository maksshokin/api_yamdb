from api.serializers import (
    PatchMeSerializer,
    UserSerializer,
    SingUpSerializer,
    ReviewSerializer,
    TokenSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    CommentSerializer
)
from api.permissions import IsSuperUserOrAdmin, IsOwnerOrReadOnly, IsOwnerOrStaff
from api_yamdb.settings import EMAIL
from reviews.models import (
    User,
    Category,
    Genre,
    Review,
    Title,
    Comment,
)

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, viewsets, status, permissions, generics, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination


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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = (UserSerializer,)
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
    )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me',
    )
    def get_user_info(self, request):
        if request.method == 'GET':
            serializer = PatchMeSerializer(request.user,)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = PatchMeSerializer(request.user, data=request.data,)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = TokenSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)

        if default_token_generator.check_token(user, confirmation_code):
            token = RefreshToken.for_user(user).access_token
            message = {'token': str(token)}
            return Response(message, status=status.HTTP_200_OK)
        message = {'confirmation_code': 'Неверный код подтверждения'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


class SingUpViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SingUpSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SingUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            from_email=EMAIL,
            recipient_list=(user.email,),
            fail_silently=False,
            subject='Код подтверждения',
            message=f'Код подтверждения: {confirmation_code}',
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsSuperUserOrAdmin,)
    queryset = Category.objects.all().order_by('name')


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    queryset = Genre.objects.all().order_by('name')
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    queryset = Title.objects.all().order_by('name')


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Comment.objects.all().order_by('-pub_date')

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)

    def get_object(self):
        review_id = self.kwargs.get('review_id')
        queryset = self.filter_queryset(Comment.objects.filter(review_id=review_id))
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    