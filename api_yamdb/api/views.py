from api.serializers import (
    AdminSerializer,
    NotAdminSerializer,
    SingUpSerializer,
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
    Title
)

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me')
    def user_info(self, request):
        serializer = AdminSerializer(request.user)
        if request.method == 'GET':
            return Response(serializer.data)
        if request.user.is_admin:
            serializer = AdminSerializer(
                request.user,
                data=request.data,
                partial=True
            )
        else:
            serializer = NotAdminSerializer(
                request.user,
                data=request.data,
                partial=True
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class TokenViewSet(viewsets.GenericViewSet):
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

class SingUpViewSet(viewsets.GenericViewSet):
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
    permission_classes = [permissions.IsAdminUser]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAdminUser]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [permissions.IsAdminUser]
