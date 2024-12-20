from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import(
    UserViewSet,
    TokenViewSet,
    SingUpViewSet,
    CategoryViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet
)

v1_router = SimpleRouter()

v1_router.register(
    'users',
    UserViewSet,
    basename='users'
)
v1_router.register(
    r'categories',
    CategoryViewSet,
    basename='categories'
)
v1_router.register(
    r'genres',
    GenreViewSet,
    basename='genres'
)
v1_router.register(
    r'titles',
    TitleViewSet,
    basename='titles'
)
v1_router.register(
    r'titles/(
    ?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
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
