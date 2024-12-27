from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UserViewSet, singup, token)

v1_router = DefaultRouter()

v1_router.register(
    'users',
    UserViewSet,
    basename='users'
)
v1_router.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
v1_router.register(
    'genres',
    GenreViewSet,
    basename='genres'
)
v1_router.register(
    'titles',
    TitleViewSet,
    basename='titles'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

auth_urls = [
    path('signup/', singup, name='singup'),
    path('token/', token, name='token'),
]

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('', include(v1_router.urls)),
]
