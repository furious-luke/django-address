# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("street_number", models.CharField(max_length=20, blank=True)),
                ("route", models.CharField(max_length=100, blank=True)),
                ("raw", models.CharField(max_length=200)),
                ("formatted", models.CharField(max_length=200, blank=True)),
                ("latitude", models.FloatField(null=True, blank=True)),
                ("longitude", models.FloatField(null=True, blank=True)),
            ],
            options={
                "ordering": ("locality", "route", "street_number"),
                "verbose_name_plural": "Addresses",
            },
        ),
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(unique=True, max_length=40, blank=True)),
                ("code", models.CharField(max_length=2, blank=True)),
            ],
            options={
                "ordering": ("name",),
                "verbose_name_plural": "Countries",
            },
        ),
        migrations.CreateModel(
            name="Locality",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=165, blank=True)),
                ("postal_code", models.CharField(max_length=10, blank=True)),
            ],
            options={
                "ordering": ("state", "name"),
                "verbose_name_plural": "Localities",
            },
        ),
        migrations.CreateModel(
            name="State",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=165, blank=True)),
                ("code", models.CharField(max_length=3, blank=True)),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="states",
                        to="address.Country",
                    ),
                ),
            ],
            options={
                "ordering": ("country", "name"),
            },
        ),
        migrations.AddField(
            model_name="locality",
            name="state",
            field=models.ForeignKey(
                on_delete=models.CASCADE, related_name="localities", to="address.State"
            ),
        ),
        migrations.AddField(
            model_name="address",
            name="locality",
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name="addresses",
                blank=True,
                to="address.Locality",
                null=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="state",
            unique_together=set([("name", "country")]),
        ),
        migrations.AlterUniqueTogether(
            name="locality",
            unique_together=set([("name", "state")]),
        ),
    ]
