from django.urls import path

from .views import AddressJS

urlpatterns = [
    path('address.js', AddressJS.as_view(), name="address.js"),
]
