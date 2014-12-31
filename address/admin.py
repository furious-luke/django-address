from django.contrib import admin

from .models import Address, Country, Locality, State


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code')


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code')


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    search_fields = ('name', 'postal_code')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    search_fields = ('name',)
