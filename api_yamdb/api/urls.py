from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
    TokenViewSet,
    SingUpViewSet,
    CategoryViewSet,
    GenreViewSet,
    ReviewListCreateView,
    ReviewRetrieveUpdateDestroyView,
    TitleViewSet
)

v1_router = DefaultRouter()

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
    path(
        'titles/<int:title_id>/reviews/',
        ReviewListCreateView.as_view(),
        name='review-list'
    ),
    path('titles/<int:title_id>/reviews/<int:pk>/',
        ReviewRetrieveUpdateDestroyView.as_view(),
        name='review-detail'),
    path('', include(v1_router.urls)),
]
