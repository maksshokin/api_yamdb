from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import ReviewViewSet, CategoryViewSet, GenreViewSet, TitleViewSet, UserViewSet


v1_router = SimpleRouter()
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
v1_router.register(r'categories', CategoryViewSet, basename='categories')
v1_router.register(r'genres', GenreViewSet, basename='genres')
v1_router.register(r'titles', TitleViewSet, basename='titles')
v1_router.register(
    'users',
    UserViewSet,
    basename='users'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
