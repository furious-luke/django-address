# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table(u'address_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
        ))
        db.send_create_signal(u'address', ['Country'])

        # Adding model 'State'
        db.create_table(u'address_state', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=165, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(related_name='states', to=orm['address.Country'])),
        ))
        db.send_create_signal(u'address', ['State'])

        # Adding unique constraint on 'State', fields ['name', 'country']
        db.create_unique(u'address_state', ['name', 'country_id'])

        # Adding model 'Locality'
        db.create_table(u'address_locality', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=165, blank=True)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(related_name='localities', to=orm['address.State'])),
        ))
        db.send_create_signal(u'address', ['Locality'])

        # Adding unique constraint on 'Locality', fields ['name', 'state']
        db.create_unique(u'address_locality', ['name', 'state_id'])

        # Adding model 'Address'
        db.create_table(u'address_address', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street_address', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('locality', self.gf('django.db.models.fields.related.ForeignKey')(related_name='addresses', to=orm['address.Locality'])),
            ('formatted', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'address', ['Address'])


    def backwards(self, orm):
        # Removing unique constraint on 'Locality', fields ['name', 'state']
        db.delete_unique(u'address_locality', ['name', 'state_id'])

        # Removing unique constraint on 'State', fields ['name', 'country']
        db.delete_unique(u'address_state', ['name', 'country_id'])

        # Deleting model 'Country'
        db.delete_table(u'address_country')

        # Deleting model 'State'
        db.delete_table(u'address_state')

        # Deleting model 'Locality'
        db.delete_table(u'address_locality')

        # Deleting model 'Address'
        db.delete_table(u'address_address')


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
            'Meta': {'ordering': "('state', 'name')", 'unique_together': "(('name', 'state'),)", 'object_name': 'Locality'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '165', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
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