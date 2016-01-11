# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.BigIntegerField()),
                ('long_name', models.CharField(blank=True, max_length=256)),
                ('short_name', models.CharField(blank=True, max_length=256)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='address.Component')),
            ],
        ),
        migrations.AddField(
            model_name='address',
            name='components',
            field=models.ManyToManyField(blank=True, to='address.Component'),
        ),
        migrations.AddField(
            model_name='address',
            name='height',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='address',
            name='formatted',
            field=models.CharField(max_length=256, default='', blank=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='street_number',
            field=models.CharField(max_length=20, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='route',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='raw',
            field=models.CharField(max_length=256, default='', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='component',
            unique_together=set([('parent', 'kind', 'long_name')]),
        ),
    ]
