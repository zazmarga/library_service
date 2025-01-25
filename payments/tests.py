from datetime import datetime, timedelta

from django.contrib.auth import get_user_model

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from borrowing.models import Borrowing
from payments.models import Payment

PAYMENTS_URL = reverse("payments:payment-list")


class UnAuthenticatedPaymentApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_and_detail_payment_unauthorized(self):
        response = self.client.get(PAYMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345",
        )
        self.client.force_authenticate(user=self.user)
        self.book = Book.objects.create(
            title="Test Book Title",
            author="Test Author",
            inventory=2,
            daily_fee=1.00,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=datetime.today().date(),
            expected_return_date=datetime.today().date() + timedelta(days=5),
            book=self.book,
            user=self.user,
        )
        self.payment = Payment.objects.create(
            status="PAID",
            type_pay="PAYMENT",
            borrowing=self.borrowing,
            session_url="https://example.com",
            session_id="TEST123session_id",
            money_to_pay=3.00,
        )

    def test_list_and_detail_payment_only_own(self):
        other_client = APIClient()
        other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="other12345",
        )
        other_client.force_authenticate(user=other_user)
        other_borrowing = Borrowing.objects.create(
            borrow_date=datetime.today().date(),
            expected_return_date=datetime.today().date() + timedelta(days=5),
            book=self.book,
            user=other_user,
        )
        other_payment = Payment.objects.create(
            status="PAID",
            type_pay="PAYMENT",
            borrowing=other_borrowing,
            session_url="https://other_example.com",
            session_id="other_TEST123session_id",
            money_to_pay=2.00,
        )

        self.assertEqual(len(Payment.objects.all()), 2)

        response = self.client.get(PAYMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.payment.id)

        url = f"{PAYMENTS_URL}{other_payment.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = f"{PAYMENTS_URL}{self.payment.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_payment_forbidden(self):
        payload = {
            "status": "PENDING",
            "type_pay": "FINE",
            "borrowing": self.borrowing,
            "money_to_pay": 0.75,
        }
        response = self.client.post(PAYMENTS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.book = Book.objects.create(
            title="Test Book Title",
            author="Test Author",
            inventory=2,
            daily_fee=1.00,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=datetime.today().date(),
            expected_return_date=datetime.today().date() + timedelta(days=5),
            book=self.book,
            user=self.user,
        )
        self.payment = Payment.objects.create(
            status="PAID",
            type_pay="PAYMENT",
            borrowing=self.borrowing,
            session_url="https://example.com",
            session_id="TEST123session_id",
            money_to_pay=3.00,
        )

    def test_list_and_detail_payment_all_list(self):
        other_client = APIClient()
        other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="other12345",
        )
        other_client.force_authenticate(user=other_user)
        other_borrowing = Borrowing.objects.create(
            borrow_date=datetime.today().date(),
            expected_return_date=datetime.today().date() + timedelta(days=5),
            book=self.book,
            user=other_user,
        )
        other_payment = Payment.objects.create(
            status="PAID",
            type_pay="PAYMENT",
            borrowing=other_borrowing,
            session_url="https://other_example.com",
            session_id="other_TEST123session_id",
            money_to_pay=2.00,
        )

        self.assertEqual(len(Payment.objects.all()), 2)

        response = self.client.get(PAYMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        url = f"{PAYMENTS_URL}{other_payment.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
