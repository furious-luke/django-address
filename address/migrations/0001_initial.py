# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('formatted', models.CharField(max_length=256)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kind', models.PositiveIntegerField()),
                ('long_name', models.CharField(max_length=256, blank=True)),
                ('short_name', models.CharField(max_length=10, blank=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='address.Component', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='address',
            name='components',
            field=models.ManyToManyField(to='address.Component'),
        ),
        migrations.AlterUniqueTogether(
            name='component',
            unique_together=set([('parent', 'kind', 'long_name')]),
        ),
    ]
