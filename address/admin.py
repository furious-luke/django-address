from django.contrib import admin
import models


class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code')

admin.site.register(models.Country, CountryAdmin)


class StateAdmin(admin.ModelAdmin):
    search_fields = ('name', 'code')

admin.site.register(models.State, StateAdmin)


class LocalityAdmin(admin.ModelAdmin):
    search_fields = ('name', 'postal_code')
    list_display = ('state', 'postal_code', 'name')

admin.site.register(models.Locality, LocalityAdmin)


class AddressAdmin(admin.ModelAdmin):
    search_fields = ('name',)

admin.site.register(models.Address, AddressAdmin)
