from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(editable=False)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowed")
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="borrowings"
    )

    def clean(self):
        if self.borrow_date is None:
            self.borrow_date = datetime.today().date()
        if self.expected_return_date and self.expected_return_date <= self.borrow_date:
            raise ValidationError("Expected return date must be after borrow date.")
        if self.actual_return_date:
            if self.actual_return_date < self.borrow_date:
                raise ValidationError(
                    "Actual return date cannot be before borrow date."
                )

    def __str__(self):
        return f"{self.user.email} borrowing {self.book}"
