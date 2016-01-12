# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from address.operations import ConvertAddresses


def get_addresses(apps, schema_editor, geolocate):
    """Load addresses from your database, converting each to
    an address string that can be used in a geolocation lookup.
    """

    ex = apps.get_model('example.Example')
    for inst in ex.objects.all():

        # Get the string of the old address.
        old_addr = str(inst.old_address)

        # Perform a lookup to convert the string into a
        # django-address Address object.
        new_addr = geolocate(old_addr)

        # Now you can store the address in your system.
        inst.address = new_addr
        inst.save()


class Migration(migrations.Migration):

    dependencies = [
        ('example', '0004_example_address'),
    ]

    operations = [
        ConvertAddresses(get_addresses),
    ]
