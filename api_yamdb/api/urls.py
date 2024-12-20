from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import(
    UserViewSet,
    TokenViewSet,
    SingUpViewSet
)

v1_router = SimpleRouter()

v1_router.register(
    'users',
    UserViewSet,
    basename='users'
)

urlpatterns = [
    path(
        'auth/signup/',
        SingUpViewSet.as_view({'post': 'post'}),
        name='signup'
    ),
    path(
        'auth/token/',
        TokenViewSet.as_view({'post': 'post'}),
        name='token'
    ),
    path('', include(v1_router.urls)),
]