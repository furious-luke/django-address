# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for l in orm.Locality.objects.all():
            if not l.name:
                l.name = None
                l.save()
            if not l.postal_code:
                l.postal_code = None
                l.save()

    def backwards(self, orm):
        for l in orm.Locality.objects.all():
            if not l.name:
                l.name = ''
                l.save()
            if not l.postal_code:
                l.postal_code = ''
                l.save()

    models = {
        u'address.address': {
            'Meta': {'ordering': "('locality', 'street_address')", 'object_name': 'Address'},
            'formatted': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'locality': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'to': u"orm['address.Locality']"}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'street_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'address.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'blank': 'True'})
        },
        u'address.locality': {
            'Meta': {'ordering': "('state', 'postal_code', 'name')", 'unique_together': "(('name', 'state', 'postal_code'),)", 'object_name': 'Locality'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('address.models.NullCharField', [], {'max_length': '165', 'null': 'True', 'blank': 'True'}),
            'postal_code': ('address.models.NullCharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'localities'", 'to': u"orm['address.State']"})
        },
        u'address.state': {
            'Meta': {'ordering': "('country', 'name')", 'unique_together': "(('name', 'country'),)", 'object_name': 'State'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'states'", 'to': u"orm['address.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '165', 'blank': 'True'})
        }
    }

    complete_apps = ['address']
    symmetrical = True
