# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from geopy.geocoders import GoogleV3
from address.models import to_python
# from address.utils import query_yes_no


def convert_addresses(apps, schema_editor):
    geolocator = GoogleV3(api_key=getattr(settings, 'GOOGLE_API_KEY', None), timeout=60)
    address_model = apps.get_model('dj_address.address')
    component_model = apps.get_model('dj_address.component')
    for obj in address_model.objects.all():
        orig_addr = obj.raw if obj.raw else obj.formatted
        addr = to_python(orig_addr,
                         instance=obj,
                         address_model=address_model,
                         component_model=component_model)
        # location = geolocator.geocode(orig_addr)
        # if location:
        #     addr = to_python(location.raw,
        #                      instance=obj,
        #                      address_model=address_model,
        #                      component_model=component_model)
        # if not location:
        #     raise Exception('Failed to convert address: %s'%repr(orig_addr))
        # new_addr = location.raw['formatted_address']
        # keep = True
        # if orig_addr != new_addr:
        #     six.print_('Converted address does not match original: %s -- %s'%(repr(orig_addr), repr(new_addr)))
        #     keep = query_yes_no('Use new value?')
        # if keep:
        #     addr = to_python(location.raw, obj, address_model, component_model)


class Migration(migrations.Migration):

    dependencies = [
        ('dj_address', '0002_create_component'),
    ]

    operations = [
        migrations.RunPython(convert_addresses),
    ]
