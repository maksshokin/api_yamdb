from api.serializers import UserSerializer, NotAdminSerializer
from api.permissions import IsSuperUserOrAdmin
from api_yamdb.settings import EMAIL
from reviews.models import User


from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


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
        if request.method == 'GET':
            return Response(serializer.data)
        if request.user.is_admin:
            serializer = UserSerializer(
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
    pass

class SingUpViewSet(viewsets.GenericViewSet):
    pass