import asyncio
from datetime import datetime

from django.db import transaction
from rest_framework import mixins, viewsets, serializers, status
from rest_framework.response import Response

from borrowing.bot_helper import send_message, ADMIN_CHAT_ID
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingRetrieveSerializer,
)
from payments.models import Payment
from payments.stripe_helper import create_stripe_payment_session


class BorrowingView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user").prefetch_related(
        "payments"
    )
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return BorrowingRetrieveSerializer
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

            session_id, session_url, money_to_pay = create_stripe_payment_session(
                borrowing
            )

            formatted_date = datetime.today().strftime("%d-%m-%Y  %H:%M")
            expected_return_date = expected_return_date.strftime("%d-%m-%Y")
            message = (
                f"{formatted_date} NEW borrowing \n"
                "----------------------------------------\n"
                f"BOOK: ** {borrowing.book.title} **  \n"
                f"has been borrowed by {borrowing.user.email}\n"
                f"expected return date: {expected_return_date}.\n"
                f"now in stock: ** {book.inventory} **\n"
            )
            asyncio.run(send_message(ADMIN_CHAT_ID, message))

        if session_id:
            payment = Payment.objects.create(
                status="PENDING",
                type_pay="PAYMENT",
                borrowing=borrowing,
                session_id=session_id,
                session_url=session_url,
                money_to_pay=money_to_pay,
            )

        serializer = self.get_serializer(borrowing)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
