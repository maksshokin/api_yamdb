from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import ReviewListCreateView, ReviewRetrieveUpdateDestroyView


router = SimpleRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewListCreateView, basename='review-list-create'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/<int:pk>/', ReviewRetrieveUpdateDestroyView, basename='review-detail'
)


urlpatterns = [
    path('', include(router.urls)),
]
