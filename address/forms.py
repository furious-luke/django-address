import logging
import sys

from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe

from .models import Address, to_python
from .widgets import AddressWidget

if sys.version > '3':
    long = int
    basestring = (str, bytes)
    unicode = str

logger = logging.getLogger(__name__)

__all__ = ['AddressWidget', 'AddressField']

if not hasattr(settings, 'GOOGLE_API_KEY') or not settings.GOOGLE_API_KEY:
    raise ImproperlyConfigured("GOOGLE_API_KEY is not configured in settings.py")


class AddressField(forms.ModelChoiceField):
    widget = AddressWidget

    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = Address.objects.none()
        super(AddressField, self).__init__(*args, **kwargs)

    def to_python(self, value):

        # Treat `None`s and empty strings as empty.
        if value is None or value == '':
            return None

        # Check for garbage in the lat/lng components.
        for field in ['latitude', 'longitude']:
            if field in value:
                if value[field]:
                    try:
                        value[field] = float(value[field])
                    except Exception:
                        raise forms.ValidationError(
                            'Invalid value for %(field)s',
                            code='invalid',
                            params={'field': field}
                        )
                else:
                    value[field] = None

        return to_python(value)
