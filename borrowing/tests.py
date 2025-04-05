from datetime import datetime, timedelta

from django.contrib.auth import get_user_model

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from borrowing.models import Borrowing


BORROWING_URL = reverse("borrowing:borrowing-list")


class UnAuthenticatedBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_and_detail_borrowing_unauthorized(self):
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTest(TestCase):
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

    def test_list_and_detail_borrowing_only_own(self):
        other_client = APIClient()
        other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="other12345",
        )
        other_client.force_authenticate(user=other_user)
        other_borrowing = Borrowing.objects.create(
            borrow_date=datetime.today().date(),
            expected_return_date=datetime.today().date() + timedelta(days=7),
            book=self.book,
            user=other_user,
        )

        self.assertEqual(len(Borrowing.objects.all()), 2)

        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing.id)

        url = f"{BORROWING_URL}{other_borrowing.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = f"{BORROWING_URL}{self.borrowing.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_borrowing_has_info_about_book(self):
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["book"]["id"], self.book.id)
        self.assertEqual(response.data[0]["book"]["title"], self.book.title)

    def test_create_borrowing_forbidden(self):
        payload = {
            "borrow_date": datetime.today().date(),
            "expected_return_date": datetime.today().date() + timedelta(days=7),
            "book": self.book,
            "user": self.user,
        }
        response = self.client.post(BORROWING_URL, payload)
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

    def test_list_all_borrowings_and_filtering_by_user_id(self):
        other_client = APIClient()
        other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="other12345",
        )
        other_client.force_authenticate(user=other_user)
        other_borrowing = Borrowing.objects.create(
            borrow_date=datetime.today().date(),
            expected_return_date=datetime.today().date() + timedelta(days=7),
            book=self.book,
            user=other_user,
        )

        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Borrowing.objects.all()), 2)
        self.assertEqual(len(Borrowing.objects.all()), len(response.data))
        self.assertEqual(other_borrowing.id, response.data[1]["id"])

        url = f"{BORROWING_URL}?user_id={other_user.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user"], other_user.id)

    def test_borrowing_list_filtering_by_is_active(self):
        borrowing2 = Borrowing.objects.create(
            borrow_date=datetime.today().date(),
            expected_return_date=datetime.today().date() + timedelta(days=3),
            book=self.book,
            user=self.user,
        )
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        url = f"{BORROWING_URL}?is_active=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        borrowing2.actual_return_date = datetime.today().date() + timedelta(days=1)
        borrowing2.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["id"], self.borrowing.id)

        borrowing2.delete()

    def test_create_borrowing(self):
        other_book = Book.objects.create(
            title="Other Book Title",
            author="Other Author",
            inventory=1,
            daily_fee=0.50,
        )
        payload = {
            "borrow_date": datetime.today().date(),
            "expected_return_date": datetime.today().date() + timedelta(days=4),
            "book": other_book.id,
            "user": self.user.id,
        }
        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(response.data)
        new_borrowing = Borrowing.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            if hasattr(new_borrowing, f"{key}_id"):
                self.assertEqual(payload[key], getattr(new_borrowing, f"{key}_id"))
            else:
                self.assertEqual(payload[key], getattr(new_borrowing, key))

    def test_delete_borrowing_not_allowed(self):
        borrowing = self.borrowing
        url = BORROWING_URL + f"{borrowing.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_return_book_inventory(self):
        prev_inventory_book = self.book.inventory
        payload = {
            "actual_return_date": datetime.today() + timedelta(days=1),
        }
        url = f"{BORROWING_URL}{self.borrowing.id}/return/"
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.book.refresh_from_db()
        new_inventory_book = self.book.inventory
        self.assertLess(prev_inventory_book, new_inventory_book)
