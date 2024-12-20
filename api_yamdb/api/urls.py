from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import(
    UserViewSet,
    TokenViewSet,
    SingUpViewSet,
    ReviewViewSet,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
)

router = SimpleRouter()

router.register(
    'users',
    UserViewSet,
    basename='users'
)

router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')

urlpatterns = [
    path(
        'auth/signup/',
        SingUpViewSet.as_view(),
        name='signup'
    ),
    path(
        'auth/token/',
        TokenViewSet.as_view(),
        name='token'
    ),
    path('', include(router.urls)),
]
