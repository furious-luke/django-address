from six import string_types
from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignObject, ReverseSingleRelatedObjectDescriptor
from django.utils.encoding import python_2_unicode_compatible

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


def _to_python(value):
    """Convert a value to an Address."""

    formatted = value.get('formatted', None)
    if not formatted:
        return None

    # Create new components, but don't save them yet.
    components = value.get('components', [])
    objs = []
    kind_table = {}
    for comp in components:
        kinds = [Component.KEY_KIND_TABLE[k] for k in comp.get('types', [])]
        kind = reduce(lambda x,y: x|y, kinds, 0)
        short_name = comp.get('short_name', '')
        long_name = comp.get('long_name', '')
        obj = Component(kind=kind, short_name=short_name, long_name=long_name)
        objs.append((obj, kinds))
        kind_table.update(dict([(k, obj) for k in kinds]))

    # If there is no country then what is this thing?
    if Component.KIND_COUNTRY not in kind_table:
        raise InconsistentDictError

    # Organise the components into a hierarchy.
    for obj, kinds in objs:
        parent = None
        while not parent and kinds:
            kinds = set(kinds)
            if Component.KIND_COUNTRY in kinds:
                kinds.remove(Component.KIND_COUNTRY)
            for kind in kinds:
                if kind in kind_table:
                    parent = kind_table[kind]
                    break
            if not parent:
                kinds = sum([hierarchy.get(k, []) for k in kinds], [])
        if not parent:
            parent = kind_table[Component.KIND_COUNTRY]
        obj.parent = parent

    # Find the lowest address components.
    roots = set([o[0] for o in objs])
    for obj, kinds in objs:
        if obj.parent:
            roots.remove(obj.parent)

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
    obj = Address.create(formatted=formatted, components=roots, latitude=lat, longitude=lng)

    return obj


def to_python(value):
    """Convert a value to an Address."""

    # Keep `None`s.
    if value is None:
        return None

    # Is it already an address object?
    if isinstance(value, Address):
        return value

    # If we have an integer, assume it is a model primary key.
    elif isinstance(value, (int, long)):
        return Address.objects.get(pk=value)

    # A string is considered a raw value.
    elif isinstance(value, string_types):
        return Address(formatted=value)

    # A dictionary of named address components.
    elif isinstance(value, dict):

        # Attempt a conversion.
        try:
            return _to_python(value)
        except InconsistentDictError:
            formatted = value.get('formatted_address', None)
            if formatted:
                return Address.objects.create(formatted=formatted)

    # Not in any of the formats I recognise.
    raise ValidationError('Invalid address value.')


@python_2_unicode_compatible
class Component(models.Model):
    """An address component."""

    KIND_STREET_ADDRESS  = 1 << 0 # 'SA'
    KIND_ROUTE           = 1 << 1 # 'RO'
    KIND_INTERSECTION    = 1 << 2 # 'IN'
    KIND_POLITICAL       = 1 << 3 # 'PO'
    KIND_COUNTRY         = 1 << 4 # 'CO'
    KIND_AAL1            = 1 << 5 # 'A1'
    KIND_AAL2            = 1 << 6 # 'A2'
    KIND_AAL3            = 1 << 7 # 'A3'
    KIND_AAL4            = 1 << 8 # 'A4'
    KIND_AAL5            = 1 << 9 # 'A5'
    KIND_COLLOQUIAL_AREA = 1 << 10 # 'CA'
    KIND_LOCALITY        = 1 << 11 # 'LO'
    KIND_WARD            = 1 << 12 # 'WA'
    KIND_SUBLOCALITY     = 1 << 13 # 'SL'
    KIND_NEIGHBORHOOD    = 1 << 14 # 'NE'
    KIND_PREMISE         = 1 << 15 # 'PR'
    KIND_SUBPREMISE      = 1 << 16 # 'SP'
    KIND_POSTAL_CODE     = 1 << 17 # 'PC'
    KIND_NATURAL_FEATURE = 1 << 18 # 'NF'
    KIND_AIRPORT         = 1 << 19 # 'AI'
    KIND_PARK            = 1 << 20 # 'PA'
    KIND_POI             = 1 << 21 # 'PI'
    KIND_FLOOR           = 1 << 22 # 'FL'
    KIND_ESTABLISHMENT   = 1 << 23 # 'ES'
    KIND_PARKING         = 1 << 24 # 'PK'
    KIND_POST_BOX        = 1 << 25 # 'PB'
    KIND_POSTAL_TOWN     = 1 << 26 # 'PT'
    KIND_ROOM            = 1 << 27 # 'RM'
    KIND_STREET_NUMBER   = 1 << 28 # 'SN'
    KIND_BUS_STATION     = 1 << 29 # 'BS'
    KIND_TRAIN_STATION   = 1 << 30 # 'TS'
    KIND_TRANSIT_STATION = 1 << 31 # 'TR'
    KIND_KEY_TABLE = {
        KIND_STREET_ADDRESS: 'street_address',
        KIND_ROUTE: 'route',
        KIND_INTERSECTION: 'intersection',
        KIND_POLITICAL: 'political',
        KIND_COUNTRY: 'country',
        KIND_AAL1: 'administrative_area_level_1',
        KIND_AAL2: 'administrative_area_level_2',
        KIND_AAL3: 'administrative_area_level_3',
        KIND_AAL4: 'administrative_area_level_4',
        KIND_AAL5: 'administrative_area_level_5',
        KIND_COLLOQUIAL_AREA: 'colloquial_area',
        KIND_LOCALITY: 'locality',
        KIND_WARD: 'ward',
        KIND_SUBLOCALITY: 'sublocality',
        KIND_NEIGHBORHOOD: 'neighborhood',
        KIND_PREMISE: 'premise',
        KIND_SUBPREMISE: 'subpremise',
        KIND_POSTAL_CODE: 'postal_code',
        KIND_NATURAL_FEATURE: 'natural_feature',
        KIND_AIRPORT: 'airport',
        KIND_PARK: 'park',
        KIND_POI: 'point_of_interest',
        KIND_FLOOR: 'floor',
        KIND_ESTABLISHMENT: 'establishment',
        KIND_PARKING: 'parking',
        KIND_POST_BOX: 'post_box',
        KIND_POSTAL_TOWN: 'postal_town',
        KIND_ROOM: 'room',
        KIND_STREET_NUMBER: 'street_number',
        KIND_BUS_STATION: 'bus_station',
        KIND_TRAIN_STATION: 'train_station',
        KIND_TRANSIT_STATION: 'transit_station',
    }
    KEY_KIND_TABLE = dict([(v, k) for k, v in KIND_KEY_TABLE.iteritems()])
    # KIND_CHOICES = [
    #     (KIND_STREET_ADDRESS, 'Street address'),
    #     (KIND_ROUTE, 'Route'),
    #     (KIND_INTERSECTION, 'Intersection'),
    #     (KIND_POLITICAL, 'Political'),
    #     (KIND_COUNTRY, 'Country'),
    #     (KIND_AAL1, 'Administrative area level 1'),
    #     (KIND_AAL2, 'Administrative area level 2'),
    #     (KIND_AAL3, 'Administrative area level 3'),
    #     (KIND_AAL4, 'Administrative area level 4'),
    #     (KIND_AAL5, 'Administrative area level 5'),
    #     (KIND_COLLOQUIAL_AREA, 'Colloquial area'),
    #     (KIND_LOCALITY, 'Locality'),
    #     (KIND_WARD, 'Ward'),
    #     (KIND_SUBLOCALITY, 'Sublocality'),
    #     (KIND_NEIGHBORHOOD, 'Neighborhood'),
    #     (KIND_PREMISE, 'Premise'),
    #     (KIND_SUBPREMISE, 'Subpremise'),
    #     (KIND_POSTAL_CODE, 'Postal code'),
    #     (KIND_NATURAL_FEATURE, 'Natural feature'),
    #     (KIND_AIRPORT, 'Airport'),
    #     (KIND_PARK, 'Park'),
    #     (KIND_POI, 'Point of interest'),
    #     (KIND_FLOOR, 'Floor'),
    #     (KIND_ESTABLISHMENT, 'Establishment'),
    #     (KIND_PARKING, 'Parking'),
    #     (KIND_POST_BOX, 'Post box'),
    #     (KIND_POSTAL_TOWN, 'Postal town'),
    #     (KIND_ROOM, 'Room'),
    #     (KIND_STREET_NUMBER, 'Street number'),
    #     (KIND_BUS_STATION, 'Bus station'),
    #     (KIND_TRAIN_STATION, 'Train station'),
    #     (KIND_TRANSIT_STATION, 'Transit station'),
    # ]

    parent     = models.ForeignKey('address.Component', related_name='children', blank=True, null=True)
    kind       = models.PositiveIntegerField()
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
        if kind == (1 << 31):
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
        for mask in self.KIND_KEY_TABLE.iterkeys():
            if self.kind & mask:
                kinds.append(mask)
        return kinds

    def get_keys(self):
        keys = []
        for mask, key in self.KIND_KEY_TABLE.iteritems():
            if self.kind & mask:
                keys.append(key)
        return keys


@python_2_unicode_compatible
class Address(models.Model):
    """A model class for an address."""

    formatted = models.CharField(max_length=256)
    components = models.ManyToManyField(Component)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return self.formatted

    def clean(self):
        if not self.formatted:
            raise ValidationError('Addresses must have a value for `formatted`.')

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
        return set(self.components.all().select_related())


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
