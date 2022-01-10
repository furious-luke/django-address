from django.contrib import admin
from django.urls import path, include

from person import views as person_views
from address import views as address_views
from address import urls as address_urls

urlpatterns = [
    path('', person_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('address/', include('address.urls')),
]
