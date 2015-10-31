from six import string_types, iteritems
from functools import reduce
from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignObject, ReverseSingleRelatedObjectDescriptor
from django.utils.encoding import python_2_unicode_compatible
from geopy.geocoders import GoogleV3
from .hierarchy import hierarchy
from .kinds import *

import logging
logger = logging.getLogger(__name__)

# Python 3 fixes.
import sys
if sys.version > '3':
    long = int
    basestring = (str, bytes)
    unicode = str

__all__ = ['Component', 'Address', 'AddressField']


class InconsistentDictError(Exception):
    pass


def _to_python(value, instance=None, address_model=None, component_model=None):
    """Convert a value to an Address."""

    if address_model is None:
        address_model = Address
    if component_model is None:
        component_model = Component

    # Get the formatted value.
    formatted = value.get('formatted_address', None)

    # Create new components, but don't save them yet.
    components = value.get('address_components', [])
    objs = []
    kind_table = {}
    for comp in components:
        kinds = [KEY_KIND_TABLE[k] for k in comp.get('types', [])]
        kind = reduce(lambda x,y: x|y, kinds, 0)
        short_name = comp.get('short_name', '')
        long_name = comp.get('long_name', '')
        if not short_name and not long_name:
            raise InconsistentDictError('No short name or long name provided.')
        obj, created = component_model.objects.get_or_create(kind=kind, short_name=short_name, long_name=long_name)
        objs.append((obj, kinds))
        kind_table.update(dict([(k, obj) for k in kinds]))

    # If there is no country then what is this thing?
    if KIND_COUNTRY not in kind_table:
        raise InconsistentDictError('No country given.')

    # Organise the components into a hierarchy.
    for obj, kinds in objs:

        # If the parent is already set don't overwrite.
        if obj.parent is not None:
            continue

        if KIND_COUNTRY in kinds:
            continue
        orig_kinds = set(kinds + [KIND_COUNTRY])
        parent = None
        while not parent and kinds:
            kinds = set(sum([hierarchy.get(k, []) for k in kinds], [])) - orig_kinds
            for kind in kinds:
                if kind in kind_table:
                    parent = kind_table[kind]
                    break
        if not parent:
            parent = kind_table[KIND_COUNTRY]
        obj.parent = parent

    # Find the lowest address components.
    roots = set([o[0] for o in objs])
    for obj, kinds in objs:
        if obj.parent:
            try:
                roots.remove(obj.parent)
            except KeyError:
                pass

    # Save the objects top-down.
    def _save(obj):
        if obj.parent:
            _save(obj.parent)
        obj.save()
    for root in roots:
        _save(root)

    # Now create the address object.
    lat = value.get('geometry', {}).get('location', {}).get('lat', None)
    lng = value.get('geometry', {}).get('location', {}).get('lng', None)
    if instance:
        obj = instance
        obj.latitude = lat
        obj.longitude = lng
        obj.formatted = formatted
        created = False
    else:
        obj, created = address_model.objects.get_or_create(formatted=formatted, latitude=lat, longitude=lng)
    obj.components = roots
    obj.save()

    return obj


def to_python(value, instance=None, address_model=None, component_model=None, geolocator=None):
    """Convert a value to an Address."""

    if address_model is None:
        address_model = Address

    # Keep `None`s.
    if value is None:
        return None

    # Is it already an address object?
    if isinstance(value, Address):
        return value

    # If we have an integer, assume it is a model primary key.
    elif isinstance(value, (int, long)):
        return address_model.objects.get(pk=value)

    # A string is considered a raw value, try to geocode and
    # if that fails then store directly.
    elif isinstance(value, string_types):
        return lookup(value, instance, address_model, component_model, geolocator)

    # A dictionary of named address components.
    elif isinstance(value, dict):

        # Attempt a conversion.
        try:
            return _to_python(value, instance, address_model, component_model)
        except InconsistentDictError:
            formatted = value.get('formatted_address', None)
            if formatted:
                return address_model.objects.create(formatted=formatted)

    # Not in any of the formats I recognise.
    raise ValidationError('Invalid address value.')


def lookup(address, instance=None, address_model=None, component_model=None, geolocator=None):
    if address_model is None:
        address_model = Address
    if geolocator is None:
        geolocator = GoogleV3(timeout=10)
    location = geolocator.geocode(address)
    if not location:
        if instance is not None:
            instance.formatted = address
            instance.components = []
            instance.latitude = None
            instance.longitude = None
            return instance
        else:
            return address_model(formatted=address)
    return to_python(location.raw, instance, component_model)


@python_2_unicode_compatible
class Component(models.Model):
    """An address component."""

    parent     = models.ForeignKey('address.Component', related_name='children', blank=True, null=True)
    kind       = models.BigIntegerField()
    long_name  = models.CharField(max_length=256, blank=True)
    short_name = models.CharField(max_length=10, blank=True)

    class Meta:
        unique_together = ('parent', 'kind', 'long_name')

    def __str__(self):
        return self.long_name

    @staticmethod
    def filter_kind(inst, kind):
        if isinstance(inst, models.Model):
            inst = inst.objects
        elif inst is None:
            inst = Component.objects
        if kind == (1 << KIND_ORDER):
            return inst.filter(kind__gte=kind)
        else:
            mask = kind << 1
            return inst.annotate(remainder=F('kind')%mask).filter(remainder__gte=kind)

    def get_geocode_entry(self):
        return {
            'long_name': self.long_name,
            'short_name': self.short_name,
            'types': self.get_keys(),
        }

    def get_kinds(self):
        kinds = []
        for mask in KIND_KEY_TABLE.iterkeys():
            if self.kind & mask:
                kinds.append(mask)
        return kinds

    def get_keys(self):
        keys = []
        for mask, key in iteritems(KIND_KEY_TABLE):
            if self.kind & mask:
                keys.append(key)
        return keys


@python_2_unicode_compatible
class Address(models.Model):
    """A model class for an address."""

    formatted  = models.CharField(max_length=256)
    components = models.ManyToManyField(Component)
    latitude   = models.FloatField(blank=True, null=True)
    longitude  = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return self.formatted

    def clean(self):
        if not self.formatted:
            raise ValidationError('Addresses must have a value for `formatted`.')

    def filter_kind(self, kind):
        res = []
        for com in self.get_components():
            if com.kind & kind:
                res.append(com)
        return res

    def filter_level(self, level):
        coms = self.get_components()
        country = self.filter_kind(KIND_COUNTRY)
        cur_level = list(country)
        while level:
            level -= 1
            next_level = []
            for c in coms:
                if c.parent in cur_level:
                    next_level.append(c)
            cur_level = next_level
        return cur_level

    def get_geocode(self):
        return {
            'address_components': [c.get_geocode_entry() for c in self.get_components()],
            'formatted_address': self.formatted,
            'geometry': {
                'location': {
                    'lat': self.latitude,
                    'lng': self.longitude,
                }
            }
        }

    def get_components(self):
        coms = set()
        unseen = list(self.components.all().select_related())
        while len(unseen):
            com = unseen.pop(0)
            coms.add(com)
            if com.parent:
                unseen.append(com.parent)
        return coms


class AddressDescriptor(ReverseSingleRelatedObjectDescriptor):
    """Override setting an address field.

    In order to call our custimised `to_python` routine each time a value
    is assigned to and AddressField we need to modify the descriptor
    class assigned to the model.
    """

    def __set__(self, inst, value):
        super(AddressDescriptor, self).__set__(inst, to_python(value))


class AddressField(models.ForeignKey):
    """An address model field.

    The address is stored as a foreign-key; AddressField inherits from
    ForeignKey but forces the related field to be `address.Address`.
    """

    description = 'An address'

    def __init__(self, **kwargs):
        kwargs['to'] = 'address.Address'
        super(AddressField, self).__init__(**kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(ForeignObject, self).contribute_to_class(cls, name, virtual_only=virtual_only)
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
