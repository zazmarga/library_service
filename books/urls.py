from django.urls import path, include
from rest_framework import routers

from books.views import BookViewSet

router = routers.DefaultRouter()


router.register("", BookViewSet)

app_name = "books"

urlpatterns = [
    path("", include(router.urls)),
]
