from six import string_types, iteritems
from functools import reduce
import logging

from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignObject
from django.conf import settings
try:
    from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor as ForwardManyToOneDescriptor
except ImportError:
    from django.db.models.fields.related import ForwardManyToOneDescriptor
from django.utils.encoding import python_2_unicode_compatible
from geopy.geocoders import GoogleV3

from .hierarchy import hierarchy
from .kinds import *
from .utils import allow_unsaved
from .consistency import get_consistency_from_parts


logger = logging.getLogger(__name__)


# Python 3 fixes.
# TODO: Remove
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

    # Get the raw and formatted values.
    formatted = value.get('formatted_address', '')
    raw = value.get('raw', formatted)

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

        # Don't create the component here. We need the hierarchy to identify
        # pre-existing components.
        obj = component_model(kind=kind, short_name=short_name, long_name=long_name)
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
        with allow_unsaved(component_model, 'parent'):
            obj.parent = parent

    # Find the lowest address components.
    roots = [o[0] for o in objs]
    for obj, kinds in objs:
        if obj.parent:
            try:
                roots.remove(obj.parent)
            except ValueError:
                pass

    # Save the objects top-down. Calculate the height while we're here.
    height = 0
    def _save(obj, h):
        if obj.parent:
            obj.parent, h = _save(obj.parent, h + 1)
        new_obj, created = component_model.objects.get_or_create(
            kind=obj.kind,
            short_name=obj.short_name, long_name=obj.long_name,
            parent=obj.parent
        )
        return new_obj, h
    for ii in range(len(roots)):
        roots[ii], h = _save(roots[ii], 0)
        height = max(height, h)

    # Calculate the consistency for the objects and raw value.
    consistent = get_consistency_from_parts(raw, [o[0] for o in objs])

    # Now create the address object.
    lat = value.get('geometry', {}).get('location', {}).get('lat', None)
    lng = value.get('geometry', {}).get('location', {}).get('lng', None)
    if instance:
        obj = instance
        obj.latitude = lat
        obj.longitude = lng
        obj.formatted = formatted
        obj.raw = raw
        obj.height = height
        obj.components = roots
        obj.consistent = consistent
        obj.save()
    else:
        obj, created = address_model.objects.get_or_create(
            raw=raw,
            defaults={
                'formatted': formatted,
                'latitude': lat,
                'longitude': lng,
                'height': height,
                'consistent': consistent,
            }
        )
        if created:
            obj.components = roots
            obj.save()

    return obj


def to_python(value, instance=None, address_model=None, component_model=None, geolocator=None):
    """Convert a value to an Address."""

    if address_model is None:
        address_model = Address

    # Keep `None`s.
    if value in [None, {}, '']:
        return None

    # Oh boy. Mother of all hacks.
    if getattr(value, '_an_unortunate_hack', False):
        return value

    # Is it already an address object?
    elif isinstance(value, address_model):
        return value

    # If we have an integer, assume it is a model primary key.
    elif isinstance(value, (int, long)):
        return address_model.objects.get(pk=value)

    # A string is considered a raw value, try to geocode and
    # if that fails then store directly.
    elif isinstance(value, string_types):

        # Don't try and lookup empty values, just set them to None.
        if value.strip() == '':
            return None

        return lookup(value, instance, address_model, component_model, geolocator)

    # A dictionary of named address components.
    elif isinstance(value, dict):

        # Attempt a conversion.
        try:
            return _to_python(value, instance, address_model, component_model)
        except InconsistentDictError:
            raw = value.get('raw', '')
            formatted = value.get('formatted_address', '')
            if raw or formatted:
                return address_model.objects.create(raw=raw, formatted=formatted)
            else:
                return None

    # Not in any of the formats I recognise.
    raise ValidationError('Invalid address value.')


def lookup(address, instance=None, address_model=None, component_model=None, geolocator=None):
    if address_model is None:
        address_model = Address
    if geolocator is None:
        geolocator = GoogleV3(api_key=getattr(settings, 'GOOGLE_API_KEY', None), timeout=10)
    location = geolocator.geocode(address)
    if not location:
        if instance is not None:
            instance.raw = address
            instance.formatted = ''
            instance.components = []
            instance.latitude = None
            instance.longitude = None
            return instance
        else:
            return address_model.objects.create(raw=address)
    location.raw['raw'] = address
    addr = to_python(location.raw, instance, address_model, component_model)
    return addr


@python_2_unicode_compatible
class Component(models.Model):
    """An address component."""

    parent     = models.ForeignKey('dj_address.Component', related_name='children', blank=True, null=True)
    kind       = models.BigIntegerField()
    long_name  = models.CharField(max_length=256, blank=True)
    short_name = models.CharField(max_length=256, blank=True)

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
        for mask in KIND_KEY_TABLE.keys():
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

    raw        = models.CharField(max_length=256, default='', blank=True)
    formatted  = models.CharField(max_length=256, default='', blank=True)
    components = models.ManyToManyField(Component, blank=True)
    height     = models.PositiveIntegerField(default=0)
    latitude   = models.FloatField(blank=True, null=True)
    longitude  = models.FloatField(blank=True, null=True)
    consistent = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return self.raw if self.raw else self.formatted

    def clean(self):
        if not self.raw and not self.formatted:
            raise ValidationError('Addresses must have at least a raw or formatted value.')

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

    @staticmethod
    def to_python(*args, **kwargs):
        global to_python
        return to_python(*args, **kwargs)


class AddressDescriptor(ForwardManyToOneDescriptor):
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
    ForeignKey but forces the related field to be `dj_address.Address`.
    """

    description = 'An address'

    def __init__(self, **kwargs):
        kwargs['to'] = 'dj_address.Address'
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
