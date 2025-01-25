from datetime import datetime

from celery import shared_task

from borrowing.models import Borrowing
from borrowing.bot_helper import send_message, ADMIN_CHAT_ID
import asyncio


@shared_task
def daily_checking_borrowings():
    borrowings = Borrowing.objects.filter(
        actual_return_date=None, expected_return_date__lt=datetime.now()
    )
    len_ = len(borrowings)
    if len_ == 0:
        asyncio.run(
            send_message(ADMIN_CHAT_ID, "** Hello! No borrowings overdue today! **")
        )
    else:
        asyncio.run(
            send_message(
                ADMIN_CHAT_ID,
                f"** Hello! There are {len_} overdue borrowing(s) today: **",
            )
        )
        date_today = datetime.today().date()

        for i, borrowing in enumerate(borrowings):
            expected_return_date = borrowing.expected_return_date
            print(borrowing)
            content = (
                f"{i + 1}: borrowing_id = {borrowing.id}, user: {borrowing.user} \n"
                f"BOOK: {borrowing.book.title} \n"
                f"expected return date: {expected_return_date} \n"
                f" ** {(date_today - expected_return_date).days} ** day(s) overdue\n"
            )
            asyncio.run(send_message(ADMIN_CHAT_ID, content))
