from django.contrib import admin
from address.models import AddressField
from address.forms import AddressWidget
from .models import Example

class ExampleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        AddressField: {'widget': AddressWidget(attrs={'style': 'width: 300px;'})}
    }

admin.site.register(Example, ExampleAdmin)
