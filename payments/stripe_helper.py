import stripe

from library_service import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_payment_session(borrowing):
    using_days = (borrowing.expected_return_date - borrowing.borrow_date).days
    money_to_pay = int(borrowing.book.daily_fee * using_days * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Borrowing book: '{borrowing.book.title}'",
                    },
                    "unit_amount": money_to_pay,  # in cents
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="https://your-domain.com/success",
        cancel_url="https://your-domain.com/cancel",
        metadata={"borrowing_id": borrowing.id},
    )
    print(f"{session.id=}, {session.url=}")

    return session.id, session.url, money_to_pay / 100
