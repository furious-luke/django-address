import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields import related
from django.utils.encoding import python_2_unicode_compatible

logger = logging.getLogger(__name__)

__all__ = ['Country', 'State', 'Locality', 'Address', 'AddressField']

##
# Convert a dictionary to an address.
##


def to_python(value):

    # Keep `None`s.
    if value is None:
        return None

    # Is it already an address object?
    if isinstance(value, Address):
        return value

    # If we have an integer, assume it is a model primary key.
    # This is mostly for Django being a cunt.
    elif isinstance(value, int):
        return value

    # A string is considered a raw value.
    elif isinstance(value, str):
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
            locality_obj = Locality(
                name=locality,
                postal_code=postal_code,
                state=state_obj)

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
                address_obj.formatted = str(address_obj)

            # Need to save.
            address_obj.save()

        # Done.
        return address_obj

    # Not in any of the formats I recognise.
    raise ValidationError('Invalid address value.')

##
# A country.
##


@python_2_unicode_compatible
class Country(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=True)
    code = models.CharField(
        max_length=255,
        blank=True)  # not unique as there are duplicates (IT)

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('name',)

    def __str__(self):
        return '%s' % (self.name or self.code)

##
# A state. Google refers to this as `administration_level_1`.
##


@python_2_unicode_compatible
class State(models.Model):
    name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey(Country, related_name='states')

    class Meta:
        unique_together = ('name', 'country')
        ordering = ('country', 'name')

    def __str__(self):
        txt = self.to_str()
        country = '%s' % self.country
        if country and txt:
            txt += ', '
        txt += country
        return txt

    def to_str(self):
        return '%s' % (self.name or self.code)

##
# A locality (suburb).
##


@python_2_unicode_compatible
class Locality(models.Model):
    name = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    state = models.ForeignKey(State, related_name='localities')

    class Meta:
        verbose_name_plural = 'Localities'
        unique_together = ('name', 'state')
        ordering = ('state', 'name')

    def __str__(self):
        txt = '%s' % self.name
        state = self.state.to_str() if self.state else ''
        if txt and state:
            txt += ', '
        txt += state
        if self.postal_code:
            txt += ' %s' % self.postal_code
        cntry = '%s' % (
            self.state.country if self.state and self.state.country else '')
        if cntry:
            txt += ', %s' % cntry
        return txt

##
# An address. If for any reason we are unable to find a matching
# decomposed address we will store the raw address string in `raw`.
##


@python_2_unicode_compatible
class Address(models.Model):
    street_number = models.CharField(max_length=255, blank=True)
    route = models.CharField(max_length=255, blank=True)
    locality = models.ForeignKey(
        Locality,
        related_name='addresses',
        blank=True,
        null=True)
    raw = models.CharField(max_length=255)
    formatted = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ('locality', 'route', 'street_number')
        unique_together = ('locality', 'route', 'street_number')

    def __str__(self):
        if self.formatted != '':
            txt = '%s' % self.formatted
        elif self.locality:
            txt = ''
            if self.street_number:
                txt = '%s' % self.street_number
            if self.route:
                if txt:
                    txt += ' %s' % self.route
            locality = '%s' % self.locality
            if txt and locality:
                txt += ', '
            txt += locality
        else:
            txt = '%s' % self.raw
        return txt

    def clean(self):
        if not self.raw:
            raise ValidationError(
                'Addresses may not have a blank `raw` field.')

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


class AddressDescriptor(related.ReverseSingleRelatedObjectDescriptor):

    def __set__(self, inst, value):
        super(AddressDescriptor, self).__set__(inst, to_python(value))

##
# A field for addresses in other models.
##


class AddressField(models.ForeignKey):
    description = 'An address'

    def __init__(self, **kwargs):
        kwargs['to'] = Address
        super(AddressField, self).__init__(**kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(
            related.ForeignObject,
            self).contribute_to_class(
            cls,
            name,
            virtual_only=virtual_only)
        setattr(cls, self.name, AddressDescriptor(self))

    # def deconstruct(self):
    #     name, path, args, kwargs = super(AddressField, self).deconstruct()
    #     del kwargs['to']
    #     return name, path, args, kwargs

    def formfield(self, **kwargs):
        from .forms import AddressField as AddressFormField
        defaults = dict(form_class=AddressFormField)
        defaults.update(kwargs)
        return super(AddressField, self).formfield(**defaults)
