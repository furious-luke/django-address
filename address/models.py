import urllib2
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignObject, ReverseSingleRelatedObjectDescriptor

import logging
logger = logging.getLogger(__name__)

__all__ = ['Country', 'State', 'Locality', 'Address', 'AddressField']

##
## Convert a dictionary to an address.
##
def to_python(value):

    # Keep `None`s.
    if value is None:
        return None

    # Is it already an address object?
    if isinstance(value, Address):
        return value

    # If we have an integer, assume it is a model primary key. This is mostly for
    # Django being a cunt.
    elif isinstance(value, (int, long)):
        return value

    # A string is considered a raw value.
    elif isinstance(value, basestring):
        obj = Address(raw=value)
        obj.save()
        return obj

    # A dictionary of named address components.
    elif isinstance(value, dict):
        raw = value.get('raw', '')
        country = value.get('country', '')
        country_code = value.get('country_code', '')
        state = value.get('state', '')
        state_code = value.get('state_code', '')
        locality = value.get('locality', '')
        postal_code = value.get('postal_code', '')
        street_number = value.get('street_number', '')
        route = value.get('route', '')
        formatted = value.get('formatted', '')
        latitude = value.get('latitude', None)
        longitude = value.get('longitude', None)

        # If there is no value (empty raw) then return None.
        if not raw:
            return None

        # Handle the country.
        try:
            country_obj = Country.objects.get(name=country)
        except Country.DoesNotExist:
            country_obj = Country(name=country, code=country_code)

        # Handle the state.
        try:
            state_obj = State.objects.get(name=state, country=country_obj)
        except State.DoesNotExist:
            country_obj.save()
            state_obj = State(name=state, code=state_code, country=country_obj)

        # Handle the locality.
        try:
            locality_obj = Locality.objects.get(name=locality, state=state_obj)
        except Locality.DoesNotExist:
            state_obj.save()
            locality_obj = Locality(name=locality, postal_code=postal_code, state=state_obj)

        # Handle the address.
        try:
            address_obj = Address.objects.get(
                street_number=street_number,
                route=route,
                locality=locality_obj
            )
        except Address.DoesNotExist:
            locality_obj.save()
            address_obj = Address(
                street_number=street_number,
                route=route,
                raw=raw,
                locality=locality_obj,
                formatted=formatted,
                latitude=latitude,
                longitude=longitude,
            )

            # If "formatted" is empty try to construct it from other values.
            if not address_obj.formatted:
                address_obj.formatted = unicode(address_obj)

            # Need to save.
            address_obj.save()

        # Done.
        return address_obj

    # Not in any of the formats I recognise.
    raise ValidationError('Invalid address value.')

##
## A country.
##
class Country(models.Model):
    name = models.CharField(max_length=40, unique=True, blank=True)
    code = models.CharField(max_length=2, blank=True) # not unique as there are duplicates (IT)

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s'%(self.name or self.code)

##
## A state. Google refers to this as `administration_level_1`.
##
class State(models.Model):
    name = models.CharField(max_length=165, blank=True)
    code = models.CharField(max_length=3, blank=True)
    country = models.ForeignKey(Country, related_name='states')

    class Meta:
        unique_together = ('name', 'country')
        ordering = ('country', 'name')

    def __unicode__(self):
        txt = self.to_str()
        country = u'%s'%self.country
        if country and txt:
            txt += u', '
        txt += country
        return txt

    def to_str(self):
        return u'%s'%(self.name or self.code)

##
## A locality (suburb).
##
class Locality(models.Model):
    name = models.CharField(max_length=165, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    state = models.ForeignKey(State, related_name='localities')

    class Meta:
        verbose_name_plural = 'Localities'
        unique_together = ('name', 'state')
        ordering = ('state', 'name')

    def __unicode__(self):
        txt = u'%s'%self.name
        state = self.state.to_str() if self.state else ''
        if txt and state:
            txt += u', '
        txt += state
        if self.postal_code:
            txt += u' %s'%self.postal_code
        cntry = u'%s'%(self.state.country if self.state and self.state.country else '')
        if cntry:
            txt += u', %s'%cntry
        return txt

##
## An address. If for any reason we are unable to find a matching
## decomposed address we will store the raw address string in `raw`.
##
class Address(models.Model):
    street_number = models.CharField(max_length=20, blank=True)
    route = models.CharField(max_length=100, blank=True)
    locality = models.ForeignKey(Locality, related_name='addresses', blank=True, null=True)
    raw = models.CharField(max_length=200)
    formatted = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ('locality', 'route', 'street_number')
        unique_together = ('locality', 'route', 'street_number')

    def __unicode__(self):
        if self.formatted != '':
            txt = u'%s'%self.formatted
        elif self.locality:
            txt = u''
            if self.street_number:
                txt = u'%s'%self.street_number
            if self.route:
                if txt:
                    txt += u' %s'%self.route
            locality = u'%s'%self.locality
            if txt and locality:
                txt += u', '
            txt += locality
        else:
            txt = u'%s'%self.raw
        return txt

    def clean(self):
        if not self.raw:
            raise ValidationError('Addresses may not have a blank `raw` field.')

    def as_dict(self):
        return dict(
            street_number=self.street_number,
            route=self.route,
            locality=self.locality.name,
            postal_code=self.locality.postal_code,
            state=self.locality.state.name,
            state_code=self.locality.state.code,
            country=self.locality.state.country.name,
            country_code=self.locality.state.country.code,
            raw=self.raw,
            formatted=self.formatted,
            latitude=self.latitude,
            longitude=self.longitude,
        )

class AddressDescriptor(ReverseSingleRelatedObjectDescriptor):

    def __set__(self, inst, value):
        super(AddressDescriptor, self).__set__(inst, to_python(value))

##
## A field for addresses in other models.
##
class AddressField(models.ForeignKey):
    description = 'An address'

    def __init__(self, **kwargs):
        super(AddressField, self).__init__(Address, **kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(ForeignObject, self).contribute_to_class(cls, name, virtual_only=virtual_only)
        setattr(cls, self.name, AddressDescriptor(self))

    def deconstruct(self):
        name, path, args, kwargs = super(AddressField, self).deconstruct()
        del kwargs['to']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        from forms import AddressField as AddressFormField
        defaults = dict(form_class=AddressFormField)
        defaults.update(kwargs)
        return super(AddressField, self).formfield(**defaults)
