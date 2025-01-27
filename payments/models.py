from django.db import models

from borrowing.models import Borrowing


class Payment(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "pending"),
        ("PAID", "paid"),
    )
    TYPE_CHOICES = (
        ("PAYMENT", "payment"),
        ("FINE", "fine"),
    )
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    type_pay = models.CharField(max_length=7, choices=TYPE_CHOICES)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=100)
    money_to_pay = models.DecimalField(decimal_places=2, max_digits=7)

    def __str__(self):
        return (
            f"Borrowing id: {self.borrowing.id}, amount: {self.money_to_pay}, "
            f"{self.type_pay}/{self.status}"
        )
