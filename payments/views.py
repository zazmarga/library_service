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
