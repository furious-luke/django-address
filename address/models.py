import urllib2
from django.db import models
from django.core.exceptions import ValidationError
from djangoutils.conv import to_address
from googlemaps import GoogleMapsError

import logging
logger = logging.getLogger(__name__)


__all__ = ['Country', 'State', 'Locality', 'Address', 'AddressField',
           'get_or_create_address']


class Country(models.Model):
    name = models.CharField(max_length=40, unique=True, blank=True)
    code = models.CharField(max_length=2, blank=True) # not unique as there are duplicates (IT)

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s'%(self.code or self.name)


class State(models.Model):
    name = models.CharField(max_length=165, blank=True)
    code = models.CharField(max_length=3, blank=True)
    country = models.ForeignKey(Country, related_name='states')

    class Meta:
        unique_together = ('name', 'country')
        ordering = ('country', 'name')

    def __unicode__(self):
        txt = u'%s'%(self.code or self.name)
        country = u'%s'%self.country
        if country and txt:
            txt += u', '
        txt += country
        return txt


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
        state = u'%s'%self.state
        if txt and state:
            txt += u', '
        txt += state
        return txt


class Address(models.Model):
    street_address = models.CharField(max_length=100, blank=True)
    locality = models.ForeignKey(Locality, related_name='addresses')
    formatted = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ('locality', 'street_address')

    def __unicode__(self):
        txt = u'%s'%self.street_address
        locality = u'%s'%self.locality
        if txt and locality:
            txt += u', '
        txt += locality
        return txt

    def as_dict(self):
        return dict(
            street_address=self.street_address,
            locality=self.locality.name,
            postal_code=self.locality.postal_code,
            state=self.locality.state.name,
            state_code=self.locality.state.code,
            country=self.locality.state.country.name,
            country_code=self.locality.state.country.code,
            formatted=self.formatted,
            latitude=self.latitude,
            longitude=self.longitude,
        )


class AddressField(models.ForeignKey):
    __metaclass__ = models.SubfieldBase
    description = 'An address'

    def __init__(self, **kwargs):
        kwargs.pop('to', None)
        self._geo_accuracy = kwargs.pop('geo_accuracy', 1)
        super(AddressField, self).__init__(Address, **kwargs)

    def str_to_dict(self, value):
        if value is None:
            return None

        # Check for a string not conforming to the serialised format.
        if isinstance(value, basestring):
            # TODO: Check for serialised version.
            # Convert to a tuple for the next part.
            value = (value,)

        # Check if we have a tuple first, because we will convert it to a dictionary
        # and let the dictionary handler deal with it.
        if isinstance(value, tuple) and len(value) >= 1:

            # Extract our name and address.
            if len(value) >= 2:
                name = value[0]
                address = value[1]
            else:
                name = None
                address = value[0]

            # Convert to a dictionary value.
            if name:
                try:
                    value = to_address(name + ' near ' + address, self._geo_accuracy)
                except GoogleMapsError, urllib2.HTTPError:
                    name = None
            if not name:
                value = to_address(address, self._geo_accuracy)

        return value

    def to_python(self, value):
        value = self.str_to_dict(value)
        if value is None:
            return None

        # Is it already an address object?
        if isinstance(value, Address):
            return value

        # If we have an integer, assume it is a model primary key. This is mostly for
        # Django being a cunt.
        elif isinstance(value, (int, long)):
            return value

        # A dictionary of named address components.
        elif isinstance(value, dict):
            country = value.get('country', '')
            country_code = value.get('country_code', '')
            state = value.get('state', '')
            state_code = value.get('state_code', '')
            locality = value.get('locality', '')
            postal_code = value.get('postal_code', '')
            street_address = value.get('street_address', '')
            formatted = value.get('formatted', '')
            latitude = value.get('latitude', '')
            longitude = value.get('longitude', '')

            # Handle the country.
            try:
                country_obj = Country.objects.get(name=country)
            except Country.DoesNotExist:
                country_obj = Country(name=country, code=country_code)

            # Handle the state.
            try:
                state_obj = State.objects.get(name=state, country=country_obj)
            except State.DoesNotExist:
                state_obj = State(name=state, code=state_code, country=country_obj)

            # Handle the locality.
            try:
                locality_obj = Locality.objects.get(name=locality, state=state_obj)
            except Locality.DoesNotExist:
                locality_obj = Locality(name=locality, postal_code=postal_code, state=state_obj)

            # Handle the address.
            try:
                address_obj = Address.objects.get(
                    street_address=street_address,
                    locality=locality_obj,
                    formatted=formatted,
                    latitude=latitude,
                    longitude=longitude,
                )
            except Address.DoesNotExist:
                address_obj = Address(
                    street_address=street_address,
                    locality=locality_obj,
                    formatted=formatted,
                    latitude=latitude,
                    longitude=longitude,
                )

            # Need to save here to help Django on it's way.
            self._do_save(address_obj)

            # If "formatted" is empty try to construct it from other values.
            if not address_obj.formatted:
                address_obj.formatted = unicode(address_obj)
                address_obj.save()

            # Done.
            return address_obj

        # Try to deserialise a string ... how?
        raise ValidationError('Invalid locality value')

    def pre_save(self, model_instance, add):
        address = getattr(model_instance, self.name)
        return self._do_save(address)

    def formfield(self, **kwargs):
        from forms import AddressField as AddressFormField
        defaults = dict(form_class=AddressFormField)
        defaults.update(kwargs)
        return super(models.ForeignKey, self).formfield(**defaults)

    def value_from_object(self, obj):
        value = getattr(obj, self.name)
        return value

    def _do_save(self, address):
        if address is None:
            return address
        address.locality.state.country.save()
        address.locality.state.country_id = address.locality.state.country.pk
        address.locality.state.save()
        address.locality.state_id = address.locality.state.pk
        address.locality.save()
        address.locality_id = address.locality.pk
        address.save()
        return address.pk


def do_save(address):
    if address is None:
        return address
    address.locality.state.country.save()
    address.locality.state.country_id = address.locality.state.country.pk
    address.locality.state.save()
    address.locality.state_id = address.locality.state.pk
    address.locality.save()
    address.locality_id = address.locality.pk
    address.save()
    return address.pk


def get_or_create_address(value, geo_accuracy=1):
    def str_to_dict(value):
        if value is None:
            return None

        # Check for a string not conforming to the serialised format.
        if isinstance(value, basestring):
            # TODO: Check for serialised version.
            # Convert to a tuple for the next part.
            value = (value,)

        # Check if we have a tuple first, because we will convert it to a dictionary
        # and let the dictionary handler deal with it.
        if isinstance(value, tuple) and len(value) >= 1:

            # Extract our name and address.
            if len(value) >= 2:
                name = value[0]
                address = value[1]
            else:
                name = None
                address = value[0]

            # Convert to a dictionary value.
            if name:
                try:
                    value = to_address(name + ' near ' + address, geo_accuracy)
                except GoogleMapsError, urllib2.HTTPError:
                    name = None
            if not name:
                value = to_address(address, geo_accuracy)

        return value

    def to_python(value):
        value = str_to_dict(value)
        if value is None:
            return None

        # Is it already an address object?
        if isinstance(value, Address):
            return value

        # If we have an integer, assume it is a model primary key. This is mostly for
        # Django being a cunt.
        elif isinstance(value, (int, long)):
            return value

        # A dictionary of named address components.
        elif isinstance(value, dict):
            country = value.get('country', '')
            country_code = value.get('country_code', '')
            state = value.get('state', '')
            state_code = value.get('state_code', '')
            locality = value.get('locality', '')
            postal_code = value.get('postal_code', '')
            street_address = value.get('street_address', '')
            formatted = value.get('formatted', '')
            latitude = value.get('latitude', '')
            longitude = value.get('longitude', '')

            # If there is nothing here then just return None.
            if not (country or country_code or state or state_code or
                    locality or postal_code or street_address or
                    latitude or longitude):
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
                state_obj = State(name=state, code=state_code, country=country_obj)

            # Handle the locality.
            try:
                locality_obj = Locality.objects.get(name=locality, state=state_obj)
            except Locality.DoesNotExist:
                locality_obj = Locality(name=locality, postal_code=postal_code, state=state_obj)

            # Handle the address.
            try:
                address_obj = Address.objects.get(
                    street_address=street_address,
                    locality=locality_obj,
                    formatted=formatted,
                    latitude=latitude,
                    longitude=longitude,
                )
            except Address.DoesNotExist:
                address_obj = Address(
                    street_address=street_address,
                    locality=locality_obj,
                    formatted=formatted,
                    latitude=latitude,
                    longitude=longitude,
                )

            # Need to save here to help Django on it's way.
            do_save(address_obj)

            # If "formatted" is empty try to construct it from other values.
            if not address_obj.formatted:
                address_obj.formatted = unicode(address_obj)
                address_obj.save()

            # Done.
            return address_obj

        # Try to deserialise a string ... how?
        raise ValidationError('Invalid locality value')

    return to_python(value)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^address\.models\.AddressField'])
except:
    pass
