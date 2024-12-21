from api.serializers import (
    UserSerializer,
    SingUpSerializer,
    ReviewSerializer,
    TokenSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer
)
from api.permissions import IsSuperUserOrAdmin
from api_yamdb.settings import EMAIL
from reviews.models import (
    User,
    Category,
    Genre,
    Review,
    Title
)

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = generics.get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (IsSuperUserOrAdmin,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = (UserSerializer,)
    permission_classes = (
        IsSuperUserOrAdmin,
        permissions.IsAuthenticated,
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
        serializer = UserSerializer(request.user, data=request.data,)
        if request.method == 'GET':
            return Response(serializer.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )



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

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny,]
        return [permissions.IsAdminUser,]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny,]
        return [permissions.IsAdminUser,]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    
    def get_permissions(self):
        if self.request.method in ['list', 'retrieve']:
            return [permissions.AllowAny,]
        return (permissions.IsAdminUser,)
