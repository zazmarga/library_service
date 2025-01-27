from datetime import datetime

from django.db import transaction
from rest_framework import mixins, viewsets, serializers, status
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowing.serializers import BorrowingSerializer, BorrowingCreateSerializer


class BorrowingView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user__id=user_id)
            is_active = self.request.query_params.get("is_active")
            if is_active and is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            return queryset
        else:
            if user.is_authenticated:
                return self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return BorrowingSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        user = validated_data.get("user")
        expected_return_date = validated_data.get("expected_return_date")
        book = validated_data.get("book")
        borrow_date = datetime.today().date()

        if book.inventory == 0:
            raise serializers.ValidationError(
                "This book is currently unavailable, please try another time."
            )

        if Borrowing.objects.filter(
            user=user, book=book, actual_return_date__isnull=True
        ).exists():
            raise serializers.ValidationError(
                "You already have one copy of this book, you cannot borrow another one."
            )

        with transaction.atomic():
            book.inventory -= 1
            book.save()
            borrowing = Borrowing.objects.create(
                borrow_date=borrow_date,
                expected_return_date=expected_return_date,
                book=book,
                user=user,
            )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
