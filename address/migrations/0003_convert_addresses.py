# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from geopy.geocoders import GoogleV3
from address.models import to_python


def convert_addresses(apps, schema_editor):
    geolocator = GoogleV3(timeout=60)
    address_model = apps.get_model('address.address')
    for obj in address_model.objects.all():
        orig_addr = obj.formatted or obj.raw
        location = geolocator.geocode(orig_addr)
        if not location:
            raise Exception('Failed to convert address: %s'%repr(orig_addr))
        new_addr = location.raw['formatted_address']
        if orig_addr != new_addr:
            raise Exception('Converted address does not match original: %s -- %s'%(repr(orig_addr), repr(new_addr)))
        addr = to_python(location.raw)
        addr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_create_component'),
    ]

    operations = [
        migrations.RunPython(convert_addresses),
    ]
