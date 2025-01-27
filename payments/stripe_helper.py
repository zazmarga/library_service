import stripe

from library_service import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_payment_session(borrowing_id):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Book Borrowing",
                    },
                    "unit_amount": 2000,  # Укажите сумму в центах
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="https://your-domain.com/success",
        cancel_url="https://your-domain.com/cancel",
        metadata={"borrowing_id": borrowing_id},
    )
    print(f"{session.id=}, {session.url=}")
    return session.id, session.url


if __name__ == "__main__":
    create_stripe_payment_session(1)
