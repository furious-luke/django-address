# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from address.operations import ConvertAddresses


def get_addresses(apps, schema_editor):
    """Load addresses from your database, converting each to
    an address string that can be used in a geolocation lookup.
    """

    my_model = apps.get_model('my_app.my_model')
    for inst in my_model.objects.all():
        yield str(inst.address)


class Migration(migrations.Migration):

    dependencies = [
        ('your_app', '0001_initial'),
    ]

    operations = [
        ConvertAddresses(get_addresses),
    ]
