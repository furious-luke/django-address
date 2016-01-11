# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0003_convert_addresses'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='locality',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='locality',
            name='state',
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='state',
            name='country',
        ),
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': 'Addresses'},
        ),
        migrations.RemoveField(
            model_name='address',
            name='locality',
        ),
        migrations.RemoveField(
            model_name='address',
            name='route',
        ),
        migrations.RemoveField(
            model_name='address',
            name='street_number',
        ),
        migrations.DeleteModel(
            name='Country',
        ),
        migrations.DeleteModel(
            name='Locality',
        ),
        migrations.DeleteModel(
            name='State',
        ),
    ]
