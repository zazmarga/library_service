from rest_framework import mixins, viewsets

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer


class BorrowingView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
