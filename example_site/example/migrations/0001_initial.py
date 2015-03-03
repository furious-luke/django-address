# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import address.models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', address.models.AddressField(to='address.Address')),
            ],
            options=None,
            bases=None,
            managers=None,
        ),
    ]
