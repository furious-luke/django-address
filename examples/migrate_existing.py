# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from address.operations import ConvertAddresses


def get_addresses(apps, schema_editor, geolocate):
    """Load addresses from your database, converting each to
    an address string that can be used in a geolocation lookup.
    """

    my_model = apps.get_model('my_app.my_model')
    for inst in my_model.objects.all():

        # Get the string of the old address.
        old_addr = str(inst.address)

        # Perform a lookup to convert the string into a
        # django-address Address object.
        new_addr = geolocate(old_addr)

        # Now you can store the address in your system.
        inst.new_address = new_addr
        inst.save()


class Migration(migrations.Migration):

    dependencies = [
        ('your_app', '0001_initial'),
    ]

    operations = [
        ConvertAddresses(get_addresses),
    ]
