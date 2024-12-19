from rest_framework import viewsets
from reviews.models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        if title_id:
            return self.queryset.filter(title_id=title_id)
        return self.queryset