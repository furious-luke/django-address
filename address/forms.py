import urllib2
from django import forms
from djangoutils.conv import to_address

try:
    from googlemaps import GoogleMapsError
except:
    pass

import logging
logger = logging.getLogger(__name__)


class AddressField(forms.CharField):
    widget = forms.TextInput(attrs={'size': '50'})

    def to_python(self, value):
        try:
            value = to_address(value)
        except GoogleMapsError:
            raise forms.ValidationError('Unable to geolocate address.')
        except urllib2.HTTPError:
            raise forms.ValidationError('Server error, try again?')
        return value
