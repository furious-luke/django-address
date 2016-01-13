import six
import json
import logging

from django import forms
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .models import Address, to_python

logger = logging.getLogger(__name__)


__all__ = ['AddressWidget', 'AddressField']


class AddressWidget(forms.TextInput):

    class Media:
        js = (
            'js/jquery.min.js',
            'https://maps.googleapis.com/maps/api/js?libraries=places&sensor=false',
            'address/js/jquery.geocomplete.js',
            'address/js/address.js'
        )

    def __init__(self, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        classes = attrs.get('class', '')
        classes += (' ' if classes else '') + 'address'
        attrs['class'] = classes
        kwargs['attrs'] = attrs
        super(AddressWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, **kwargs):

        # Can accept None, a dictionary of values, a PK, or an Address object.
        if value in (None, ''):
            ad = {}
            raw = None
        elif isinstance(value, dict):
            ad = value
            raw = ad.get('raw', ad.get('formatted_address', None))
        elif isinstance(value, six.integer_types):
            ad = Address.objects.get(pk=value)
            raw = ad.raw
            ad = ad.get_geocode()
        else:
            ad = value.get_geocode()
            raw = value.raw

        # Begin by generating the visible formatted address.
        elems = [super(AddressWidget, self).render(name, raw, attrs, **kwargs)]

        # Generate the hidden JSON field.
        elems.append('<input type="hidden" id="id_%s_geocode" name="%s_geocode" value="%s" />'%(name, name, escape(json.dumps(ad))))

        return mark_safe('\n'.join(elems))

    def value_from_datadict(self, data, files, name):
        try:
            geo = json.loads(data.get(name + '_geocode', None))
        except:
            geo = {}
        try:
            geo['raw'] = data.get(name, None)
        except:
            pass
        return geo


class AddressField(forms.ModelChoiceField):
    widget = AddressWidget

    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = Address.objects.none()
        super(AddressField, self).__init__(*args, **kwargs)

    def to_python(self, value):

        # Treat `None`s and empty strings as empty.
        if value in (None, ''):
            return None

        # Check for garbage in the lat/lng components.
        geom = value.get('geometry', {}).get('location', {})
        for field in ('lat', 'lng'):
            if field in geom:
                if geom[field]:
                    try:
                        geom[field] = float(geom[field])
                    except:
                        raise forms.ValidationError('Invalid value for %(field)s', code='invalid',
                                                    params={'field': field})
                else:
                    geom[field] = None

        return to_python(value)
