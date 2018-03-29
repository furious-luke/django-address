from django.contrib import admin
from django.urls import path

from person import views as person

urlpatterns = [
    path('', person.home, name='home'),
    path('admin/', admin.site.urls),
]
