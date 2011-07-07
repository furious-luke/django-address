import urllib2
from django import forms
from django.utils.safestring import mark_safe
from djangoutils.conv import to_address
from googlemaps import GoogleMapsError
from models import get_or_create_address

import logging
logger = logging.getLogger(__name__)


__all__ = ['AddressWidget', 'AddressField']


class AddressWidget(forms.Textarea):

    # class Media:
    #     js = ('js/jquery.min.js', 'address/js/address.js',)

    def render(self, name, value, attrs=None, **kwargs):

        # Can accept None, a dictionary of values or an Address object.
        if value is None:
            ad = {}
        elif isinstance(value, dict):
            ad = value
        else:
            ad = value.as_dict()

        elems = [
            '<ul>',
#            '<button type="button" class="address-lookup-btn">Google lookup</button>',
        ]
        components = ['street_address', 'locality', 'postal_code', 'state', 'state_code',
                      'country', 'country_code', 'latitude', 'longitude']
        for com in components:
            val = ad.get(com, '')
            if val is None:
                val = ''
            elems.extend([
                '<li>',
                '<label>%s'%com.replace('_', ' ').capitalize(),
                '<input type="text" class="textinput textInput" id="id_address-%s" name="address-%s" value="%s" />'%(com, com, val),
                '</label>',
                '</li>',
            ])
        elems.append('</ul>')
        return mark_safe(unicode('\n'.join(elems)))

    def value_from_datadict(self, data, files, name):
        ad = dict(
            street_address=data.get('address-street_address', ''),
            locality=data.get('address-locality', ''),
            postal_code=data.get('address-postal_code', ''),
            state=data.get('address-state', ''),
            state_code=data.get('address-state_code', ''),
            country=data.get('address-country', ''),
            country_code=data.get('address-country_code', ''),
            latitude=data.get('address-latitude', ''),
            longitude=data.get('address-longitude', ''),
        )
        return ad


class AddressField(forms.Field):
    widget = AddressWidget

    def to_python(self, value):
        if value is None:
            return None
        if not value['latitude']:
            value['latitude'] = None
        else:
            try:
                value['latitude'] = float(value['latitude'])
            except ValueError:
                raise forms.ValidationError('Invalid latitude.')
        if not value['longitude']:
            value['longitude'] = None
        else:
            try:
                value['longitude'] = int(value['longitude'])
            except ValueError:
                raise forms.ValidationError('Invalid longitude.')
        return get_or_create_address(value)
