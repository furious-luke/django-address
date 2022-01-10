##
# A field for addresses in other models.
##
from django.db import models
from . import models as address_models
from . import forms as address_forms


class AddressField(models.ForeignKey):
    description = 'An address'

    def __init__(self, *args, **kwargs):
        kwargs['to'] = 'address.Address'
        # The address should be set to null when deleted if the relationship could be null
        default_on_delete = models.SET_NULL if kwargs.get('null', False) else models.CASCADE
        kwargs['on_delete'] = kwargs.get('on_delete', default_on_delete)
        super(AddressField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        from address.compat import compat_contribute_to_class

        compat_contribute_to_class(self, cls, name, virtual_only)

        setattr(cls, self.name, address_models.AddressDescriptor(self))

    def formfield(self, **kwargs):
        defaults = dict(form_class=address_forms.AddressField)
        defaults.update(kwargs)
        return super(AddressField, self).formfield(**defaults)