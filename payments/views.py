from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import mixins, viewsets

from payments.models import Payment
from payments.permissions import IsAdminOrIfAuthenticatedReadOnly
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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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


def payment_success(request):
    session_id = request.GET.get("session_id")
    if session_id:
        payment = Payment.objects.get(session_id=session_id)
        payment.status = "PAID"
        payment.save()
        return render(request, "success.html")
    return HttpResponse("Payment session not found.")

def payment_cancel(request):
    return render(request, "cancel.html")
