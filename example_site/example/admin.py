from django.contrib import admin
from address.forms import AddressField, AddressWidget
from .models import Example

class ExampleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        AddressField: {'widget': AddressWidget}
    }

admin.site.register(Example, ExampleAdmin)
