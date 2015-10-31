# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from geopy.geocoders import GoogleV3
from address.models import to_python
from address.utils import query_yes_no


def convert_addresses(apps, schema_editor):
    geolocator = GoogleV3(timeout=60)
    address_model = apps.get_model('address.address')
    component_model = apps.get_model('address.component')
    for obj in address_model.objects.all():
        orig_addr = obj.formatted or obj.raw
        location = geolocator.geocode(orig_addr)
        if not location:
            raise Exception('Failed to convert address: %s'%repr(orig_addr))
        new_addr = location.raw['formatted_address']
        keep = True
        if orig_addr != new_addr:
            six.print_('Converted address does not match original: %s -- %s'%(repr(orig_addr), repr(new_addr)))
            keep = query_yes_no('Use new value?')
        if keep:
            addr = to_python(location.raw, obj, address_model, component_model)


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_create_component'),
    ]

    operations = [
        migrations.RunPython(convert_addresses),
    ]
