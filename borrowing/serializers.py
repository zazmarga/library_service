from django.contrib.auth import get_user_model
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )

    def get_payments(self, obj):
        from payments.serializers import PaymentInBorrowingListSerializer
        from payments.models import Payment

        payments = Payment.objects.filter(borrowing=obj)
        return PaymentInBorrowingListSerializer(payments, many=True).data


class BorrowingRetrieveSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )

    def get_payments(self, obj):
        from payments.serializers import PaymentInBorrowingRetrieveSerializer
        from payments.models import Payment

        payments = Payment.objects.filter(borrowing=obj)
        return PaymentInBorrowingRetrieveSerializer(payments, many=True).data


class BorrowingCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "expected_return_date",
            "book",
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "actual_return_date",
        )


class BorrowingInPaymentRetrieveSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "actual_return_date",
        )
