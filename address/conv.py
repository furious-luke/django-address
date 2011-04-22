from django.conf import settings

# Try to import googlemaps, throwing an error if we can't find it.
try:
    from googlemaps import GoogleMaps, GoogleMapsError
except:
    raise ImportError('The "googlemaps" module is required to use "django-address".')


def to_address(val):
    if val is None:
        return None

    # Throw an error if we don't have an API key.
    try:
        api_key = settings.GOOGLE_MAPS_API_KEY
    except:
        raise KeyError('Please set your Google Maps API key in your Django "settings.py" ' \
                           'under "GOOGLE_MAPS_API_KEY".')

    gmaps = GoogleMaps(settings.GOOGLE_MAPS_API_KEY)
    if isinstance(val, (list, tuple)) and len(val) >= 2:
        val = gmaps.reverse_geocode(val[0], val[1])
    else:
        val = gmaps.reverse_geocode(*gmaps.address_to_latlng(val))
    address = val['Placemark'][0]['address']
    details = val['Placemark'][0]['AddressDetails']
    country = details['Country']['CountryName']
    state = details['Country'].get('AdministrativeArea', '').get('AdministrativeAreaName', '')
    state_code = details['Country'].get('AdministrativeArea', '').get('AdministrativeAreaNameCode', '')
    locality = details['Country'].get('AdministrativeArea', '').get('Locality', '').get('LocalityName']
    postal_code = details['Country'].get('AdministrativeArea', '').get('Locality', '').get('PostalCode', '').get('PostalCodeNumber', '')
    street_address = details['Country'].get('AdministrativeArea', '').get('Locality', '').get('Thoroughfare'].get('ThoroughfareName')
    return dict(
        country=country,
        country_code=country_code,
        state=state,
        state_code=state_code,
        locality=locality,
        street_address=street_address,
        postal_code=postal_code
    )
