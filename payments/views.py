from rest_framework import mixins, viewsets

from payments.models import Payment
from payments.serializers import (
    PaymentSerializer,
    PaymentRetrieveSerializer,
)


class PaymentView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentRetrieveSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if user.is_staff:
            return queryset
        if user.is_authenticated and not user.is_staff:
            return self.queryset.filter(borrowing__user=user)
