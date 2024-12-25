from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
    CategoryViewSet,
    GenreViewSet,
    ReviewListCreateView,
    ReviewRetrievePatchDestroyView,
    TitleViewSet,
    CommentViewSet,
    singup,
    token
)

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
        singup,
        name='singup',
    ),
    path(
        'auth/token/',
        token,
        name='token'
    ),
    path(
        'titles/<int:title_id>/reviews/',
        ReviewListCreateView.as_view(),
        name='review-list'
    ),
    path(
        'titles/<int:title_id>/reviews/<int:pk>/',
        ReviewRetrievePatchDestroyView.as_view(),
        name='review-detail'
    ),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/comments/',
        CommentViewSet.as_view(actions={'get': 'list', 'post': 'create'}),
        name='create_comment'
    ),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
        CommentViewSet.as_view(
            actions={
                'get': 'retrieve',
                'delete': 'destroy',
                'patch': 'partial_update'
            }
        ),
        name='comment-detail'
    ),
    path('', include(v1_router.urls)),
]
