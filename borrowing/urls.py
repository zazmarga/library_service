from django.urls import path, include
from rest_framework import routers

from borrowing.views import BorrowingView

router = routers.DefaultRouter()
router.register("", BorrowingView)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowing"
