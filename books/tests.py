from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book

BOOK_URL = reverse("books:book-list")


class UnAuthenticatedBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = Book.objects.create(
            title="Test Book Title",
            author="Test Author",
            inventory=2,
            daily_fee=1.00,
        )

    def test_list_and_detail_books_allowed(self):
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book_id = self.book.id
        url = f"{BOOK_URL}{book_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_unauthorized(self):
        payload = {
            "title": "New book title",
            "author": "author",
            "inventory": 1,
            "daily_fee": 1.00,
        }
        response = self.client.post(BOOK_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTest(TestCase):
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

    def test_create_book_forbidden(self):
        payload = {
            "title": "New book title",
            "author": "author",
            "inventory": 1,
            "daily_fee": 1.00,
        }
        response = self.client.post(BOOK_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(TestCase):
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

    def test_create_book(self):
        payload = {
            "title": "New book title",
            "author": "author",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": 1.00,
        }
        response = self.client.post(BOOK_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=response.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_update_book(self):
        book = self.book
        url = f"{BOOK_URL}{book.id}/"
        inventory = book.inventory
        payload = {
            "title": "New book title",
            "inventory": inventory + 1,
        }
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
