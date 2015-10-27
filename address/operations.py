from django.db import migrations
from geopy.geocoders import GoogleV3
from address.models import to_python


def convert_addressess(apps, schema_editor):
    geolocator = GoogleV3(timeout=60)
    address_model = apps.get_model('address.address')
    for orig_addr in self.get_addresses():
        location = geolocator.geocode(orig_addr)
        if not location:
            raise Exception('Failed to convert address: %s'%repr(orig_addr))
        new_addr = location.raw['formatted_address']
        if orig_addr != new_addr:
            raise Exception('Converted address does not match original: %s -- %s'%(repr(orig_addr), repr(new_addr)))
        addr = to_python(location.raw, None, apps.get_model('address.component')))


class ConvertAddresses(migrations.RunPython):

    def __init__(self, get_address, *args, **kwargs):
        self.get_address = get_address
        super(ConvertAddresses, self).__init__(convert_addresses, *args, **kwargs)
