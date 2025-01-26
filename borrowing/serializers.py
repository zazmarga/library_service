from django.contrib.auth import get_user_model
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
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
