from ..pythonutils import conv
from django.conf import settings


def to_address(value):
    try:
        api_key = settings.GOOGLE_MAPS_API_KEY
    except:
        raise KeyError('Please set your Google Maps API key in your Django "settings.py" ' \
                           'under "GOOGLE_MAPS_API_KEY".')
    return conv.to_address(value, api_key)
