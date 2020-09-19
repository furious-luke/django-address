from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from address.models import *


class UnidentifiedListFilter(SimpleListFilter):
    title = 'unidentified'
    parameter_name = 'unidentified'

    def lookups(self, request, model_admin):
        return (('unidentified', 'unidentified'),)

    def queryset(self, request, queryset):
        if self.value() == 'unidentified':
            return queryset.filter(locality=None)


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
    search_fields = ('street_number', 'route', 'raw')
    list_filter = (UnidentifiedListFilter,)
