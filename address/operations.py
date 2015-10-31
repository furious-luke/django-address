import six
from django.db import migrations
from geopy.geocoders import GoogleV3
from address.models import to_python
from address.utils import query_yes_no


_get_addresses = None


def convert_addresses(apps, schema_editor):
    geolocator = GoogleV3(timeout=60)
    address_model = apps.get_model('address.address')
    component_model = apps.get_model('address.component')
    for orig_addr in _get_addresses(apps, schema_editor):
        location = geolocator.geocode(orig_addr)
        if not location:
            raise Exception('Failed to convert address: %s'%repr(orig_addr))
        new_addr = location.raw['formatted_address']
        keep = True
        if orig_addr != new_addr:
            six.print_('Converted address does not match original: %s -- %s'%(repr(orig_addr), repr(new_addr)))
            keep = query_yes_no('Use new value?')
        if keep:
            addr = to_python(location.raw, None, address_model, component_model)


class ConvertAddresses(migrations.RunPython):

    def __init__(self, get_addresses, *args, **kwargs):
        global _get_addresses
        self.get_addresses = get_addresses
        _get_addresses = get_addresses
        super(ConvertAddresses, self).__init__(convert_addresses, *args, **kwargs)
