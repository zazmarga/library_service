from rest_framework import serializers

from borrowing.serializers import BorrowingSerializer
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
    borrowing = BorrowingSerializer(read_only=True)
