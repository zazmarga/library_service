from rest_framework import serializers

from borrowing.serializers import BorrowingSerializer, BorrowingInPaymentRetrieveSerializer
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type_pay",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentRetrieveSerializer(PaymentSerializer):
    borrowing = BorrowingInPaymentRetrieveSerializer(read_only=True)


class PaymentInBorrowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
        )


class PaymentInBorrowingRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type_pay",
            "session_url",
            "session_id",
            "money_to_pay",
        )
