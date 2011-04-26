import dateutil.parser, re
from xml.dom import minidom

# Don't assume googlemaps is available.
try:
    from googlemaps import GoogleMaps, GoogleMapsError
except:
    pass


def strip_bad_unicode(value):
    if type(value) == type(u''):
        return value.replace(u'\u2019', '\'')
    return value


def to_iter(value):
    if hasattr(value, '__iter__') and not isinstance(value, dict):
        return value
    return [value]


def to_list(value):
    if value is None:
        return None
    elif isinstance(value, (str, unicode, dict)):
        return [value]
    else:
        return list(value)


def to_bool(value):
    if value is None:
        return None
    if isinstance(value, (str, unicode)):
        return not value.lower() in ['f', 'false']
    return bool(value)


def to_price(value, safe=False):
    if value is None:
        return None
    exp = r'\$\s*(\d+(?:\.\d+)?)'
    if isinstance(value, (str, unicode)):
        value = ' '.join(value.splitlines())
        if isinstance(value, unicode):
            match = re.search(exp, value, re.UNICODE)
        else:
            match = re.search(exp, value)
        if match:
            return float(match.group(1))
    try:
        return float(value)
    except:
        if safe:
            return None
        raise


def to_date(value):
    if value is None:
        return None
    dt = dateutil.parser.parse(value, fuzzy=True)
    return dt.date()


def to_time(value):
    if value is None:
        return None
    dt = dateutil.parser.parse(value, fuzzy=True)
    return dt.time()


def to_datetime(value):
    if value is None:
        return None
    dt = dateutil.parser.parse(str(value), fuzzy=True)
    return dt


def to_address(value, google_api_key):
    if value is None:
        return None
    gmaps = GoogleMaps(google_api_key)
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        if isinstance(value[0], (int, float)) and isinstance(value[1], (int, float)):
            value = gmaps.reverse_geocode(value[0], value[1])
        else:
            value = gmaps.geocode(value[0] + ' near ' + value[1])
    else:
        value = gmaps.geocode(value)
    address = value['Placemark'][0]['address']
    details = value['Placemark'][0]['AddressDetails']
    country_dict = details.get('Country', {})
    country = country_dict.get('CountryName', '')
    country_code = country_dict.get('CountryNameCode', '')
    state_dict = country_dict.get('AdministrativeArea', {})
    state = state_dict.get('AdministrativeAreaName', '')
    state_code = state_dict.get('AdministrativeAreaNameCode', '')
    locality_dict = state_dict.get('Locality', {})
    locality = locality_dict.get('LocalityName', '')
    postal_code = locality_dict.get('PostalCode', {}).get('PostalCodeNumber', '')
    street_address = locality_dict.get('Thoroughfare', {}).get('ThoroughfareName', '')
    try:
        lng, lat = value['Placemark'][0]['Point']['coordinates'][0:2]
    except:
        lng, lat = None, None
    return dict(
        country=country,
        country_code=country_code,
        state=state,
        state_code=state_code,
        locality=locality,
        street_address=street_address,
        postal_code=postal_code,
        latitude=lat,
        longitude=lng,
    )


# def to_timezone(value, precise=False):
#     if value is None:
#         return None
#     latlng = to_latlng(value)
#     if precise:
#         url = "%s/%s/%s"%('http://www.earthtools.org/timezone', latlng[0], latlng[1])
#         response = urllib2.urlopen(url).read()
#         xml = minidom.parseString(response)
#         offset = float(xml.getElementsByTagName('offset')[0].childNodes[0].nodeValueue)
#     else:
#         offset = int(round(latlng[1]/15.0))
#     return offset


def to_url(value):
    # TODO: More checks/formatting.
    if value is None:
        return None
    return str(value)


def coerce_field(record, field, coer, **kwargs):
    if field in record:
        record[field] = coer(record[field], **kwargs)
    elif 'default' in kwargs:
        default = kwargs.pop('default')
        record[field] = coer(default, **kwargs)
    if field in record and record[field] is None:
        del record[field]


def int_field(record, field, **kwargs):
    coerce_field(record, field, int, **kwargs)


def unicode_field(record, field, **kwargs):
    coerce_field(record, field, unicode, **kwargs)


def bool_field(record, field, **kwargs):
    coerce_field(record, field, to_bool, **kwargs)


def price_field(record, field, **kwargs):
    coerce_field(record, field, to_price, **kwargs)


def date_field(record, field, **kwargs):
    coerce_field(record, field, to_date, **kwargs)


def time_field(record, field, **kwargs):
    coerce_field(record, field, to_time, **kwargs)


def datetime_field(record, field, **kwargs):
    coerce_field(record, field, to_datetime, **kwargs)


def address_field(record, field, **kwargs):
    coerce_field(record, field, to_address, **kwargs)


# def timezone_field(record, field, **kwargs):
#     coerce_field(record, field, to_timezone, **kwargs)


def url_field(record, field, **kwargs):
    coerce_field(record, field, to_url, **kwargs)
