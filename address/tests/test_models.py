from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Model
from django.conf import settings
from address.models import *
from address.models import to_python, _to_python, InconsistentDictError
from address.kinds import *


def au_factory():
    au, created = Component.objects.get_or_create(kind=KIND_COUNTRY | KIND_POLITICAL, long_name='Australia', short_name='AU')
    vic, created = Component.objects.get_or_create(kind=KIND_AAL1 | KIND_POLITICAL, long_name='Victoria', short_name='VIC', parent=au)
    Component.objects.get_or_create(kind=KIND_AAL1, long_name='Tasmania', short_name='TAS', parent=au)
    nc, created = Component.objects.get_or_create(kind=KIND_LOCALITY, long_name='Northcote', parent=vic)
    pc, created = Component.objects.get_or_create(kind=KIND_POSTAL_CODE, long_name='3070', parent=nc)
    addr, created = Component.objects.get_or_create(kind=KIND_STREET_ADDRESS, long_name='2 Something Avenue', parent=pc)
    return addr


def nz_factory():
    addr, created = Component.objects.get_or_create(kind=KIND_COUNTRY, long_name='New Zealand', short_name='NZ')
    return addr


def au_address_factory():
    com = au_factory()
    addr = Address(formatted='2 Something Avenue, Northcote 3070, Victoria, Australia', latitude=1.1, longitude=2.2)
    addr.save()
    addr.components.add(com)
    return addr


class ComponentTestCase(TestCase):

    def test_unique_constraint(self):
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            au_factory()
            self.assertRaises(IntegrityError, au_factory)
            nz_factory()
            self.assertRaises(IntegrityError, nz_factory)

    def test_filter_kind_on_country(self):
        au_factory()
        res = [r.long_name for r in Component.filter_kind(Component.objects, KIND_COUNTRY)]
        self.assertEqual(res, ['Australia'])

    def test_filter_kind_on_aal1(self):
        au_factory()
        cmps = Component.filter_kind(Component.objects, KIND_AAL1)
        res = [r.long_name for r in cmps]
        self.assertEqual(res, ['Victoria', 'Tasmania'])

    def test_filter_kind_on_political(self):
        au_factory()
        res = [r.long_name for r in Component.filter_kind(Component.objects, KIND_POLITICAL)]
        self.assertEqual(res, ['Australia', 'Victoria'])

    def test_get_geocode_entry(self):
        au_factory()
        vic = Component.objects.filter(long_name='Victoria')[0]
        self.assertEqual(vic.get_geocode_entry(), {
            'long_name': 'Victoria',
            'short_name': 'VIC',
            'types': ['political', 'administrative_area_level_1'],
        })


class AddressTestCase(TestCase):

    def test_clean_throws_without_formatted(self):
        addr = Address()
        self.assertRaises(ValidationError, addr.clean)

    def test_clean_accepts_formatted(self):
        addr = Address(formatted='anything')
        addr.clean()

    def test_get_geocode_has_components(self):
        addr = au_address_factory()
        geo = addr.get_geocode()
        self.assertEqual(
            geo.get('address_components', None),
            [
                {
                    'types': ['political', 'country'],
                    'short_name': 'AU',
                    'long_name': 'Australia'
                },
                {
                    'types': ['political', 'administrative_area_level_1'],
                    'short_name': 'VIC',
                    'long_name': 'Victoria'
                },
                {
                    'types': ['locality'],
                    'short_name': '',
                    'long_name': 'Northcote'
                },
                {
                    'types': ['postal_code'],
                    'short_name': '',
                    'long_name': '3070'
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '2 Something Avenue'
                },
            ]
        )

    def test_get_geocode_has_formatted_address(self):
        addr = au_address_factory()
        geo = addr.get_geocode()
        self.assertEqual(geo.get('formatted_address', None), '2 Something Avenue, Northcote 3070, Victoria, Australia')

    def test_get_geocode_has_geometry(self):
        addr = au_address_factory()
        geo = addr.get_geocode()
        self.assertEqual(
            geo.get('geometry', None),
            {
                'location': {
                    'lat': 1.1,
                    'lng': 2.2,
                }
            }
        )

    def test_get_components_includes_related(self):
        addr = au_address_factory()
        self.assertEqual(len(addr.get_components()), 5)

    def test_filter_kind(self):
        addr = au_address_factory()
        self.assertEqual(addr.filter_kind(KIND_COUNTRY), list(Component.objects.filter(long_name='Australia')))
        self.assertEqual(addr.filter_kind(KIND_AAL1), [Component.objects.get(long_name='Victoria')])

    def test_filter_level(self):
        addr = au_address_factory()
        self.assertEqual(addr.filter_level(0), [Component.objects.get(long_name='Australia')])
        self.assertEqual(addr.filter_level(1), [Component.objects.get(long_name='Victoria')])
        self.assertEqual(addr.filter_level(2), [Component.objects.get(long_name='Northcote')])
        self.assertEqual(addr.filter_level(3), [Component.objects.get(long_name='3070')])

    def test_filter_level_returns_empty_when_too_high(self):
        addr = au_address_factory()
        self.assertEqual(addr.filter_level(100), [])


class ToPythonTestCase(TestCase):

    def test_none_returns_none(self):
        self.assertEqual(to_python(None), None)

    def test_address_returns_address(self):
        addr = au_address_factory()
        self.assertEqual(to_python(addr), addr)

    def test_integer_treated_as_pk(self):
        addr = au_address_factory()
        self.assertEqual(to_python(addr.pk), addr)

    def test_string_uses_geocoder(self):
        addr = to_python('95 Clauscen Street, Fitzroy North, Australia')
        if addr.components:
            self.assertEqual(addr.formatted, '95 Clauscen St, Fitzroy North VIC 3068, Australia')
            self.assertEqual(addr.filter_kind(KIND_COUNTRY)[0].long_name, 'Australia')
        else:
            self.warning('Geocoding test did not locate address.')

    def test_inconsistent_dict_uses_formatted(self):
        addr = to_python({'street_address': 'hello world', 'formatted_address': 'full hello world'})
        self.assertEqual(addr.raw, 'full hello world')

    def test_no_formatted_raises_error(self):
        self.assertRaises(ValidationError, to_python, {'street_address': 'hello world'})


class _ToPythonTestCase(TestCase):

    def test_no_country_raises_error(self):
        self.assertRaises(InconsistentDictError, _to_python, {})

    def test_hierarchy_is_created(self):
        addr = _to_python({
            'formatted_address': 'test',
            'address_components': [
                {
                    'types': ['administrative_area_level_1', 'political'],
                    'short_name': 'VIC',
                    'long_name': 'Victoria',
                },
                {
                    'types': ['country'],
                    'short_name': 'AU',
                    'long_name': 'Australia',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '2 Blah Street',
                }
            ]
        })
        self.assertEqual(len(addr.components.all()), 1)
        com = addr.components.all()[0]
        self.assertEqual(com.long_name, '2 Blah Street')
        com = com.parent
        self.assertEqual(com.long_name, 'Victoria')
        com = com.parent
        self.assertEqual(com.long_name, 'Australia')
        com = com.parent
        self.assertEqual(com, None)

    def test_root_components_are_found(self):
        addr = _to_python({
            'formatted_address': 'test',
            'address_components': [
                {
                    'types': ['country'],
                    'short_name': 'AU',
                    'long_name': 'Australia',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '2 Blah Street',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '5 Another Ave',
                }
            ]
        })
        self.assertEqual(len(addr.components.all()), 2)
        self.assertEqual(
            set([c.long_name for c in addr.components.all()]),
            set(['2 Blah Street', '5 Another Ave'])
        )

    def test_formatted_address_is_used(self):
        addr = _to_python({
            'formatted_address': 'test',
            'address_components': [
                {
                    'types': ['country'],
                    'short_name': 'AU',
                    'long_name': 'Australia',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '2 Blah Street',
                },
            ]
        })
        self.assertEqual(addr.formatted, 'test')

    def test_geometry_is_used(self):
        addr = _to_python({
            'formatted_address': 'test',
            'address_components': [
                {
                    'types': ['country'],
                    'short_name': 'AU',
                    'long_name': 'Australia',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '2 Blah Street',
                }
            ],
            'geometry': {
                'location': {
                    'lat': 1.1,
                    'lng': 2.2,
                }
            }
        })
        self.assertEqual(addr.latitude, 1.1)
        self.assertEqual(addr.longitude, 2.2)

    def test_missing_short_and_long_name_raises_error(self):
        self.assertRaises(InconsistentDictError, _to_python, {
            'formatted_address': 'test',
            'address_components': [
                {
                    'types': ['country'],
                    'short_name': '',
                    'long_name': '',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '2 Blah Street',
                }
            ]
        })

    def test_components_not_duplicated(self):
        addr0 = _to_python({
            'formatted_address': 'test0',
            'address_components': [
                {
                    'types': ['country'],
                    'short_name': 'AU',
                    'long_name': 'Australia',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '2 Blah Street',
                }
            ]
        })
        addr1 = _to_python({
            'formatted_address': 'test1',
            'address_components': [
                {
                    'types': ['country'],
                    'short_name': 'AU',
                    'long_name': 'Australia',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '3 Blah Street',
                }
            ]
        })
        self.assertEqual(addr0.filter_kind(KIND_COUNTRY)[0], addr1.filter_kind(KIND_COUNTRY)[0])

    def test_addresses_not_duplicated(self):
        addr0 = _to_python({
            'formatted_address': 'test0',
            'address_components': [
                {
                    'types': ['country'],
                    'short_name': 'AU',
                    'long_name': 'Australia',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '2 Blah Street',
                }
            ]
        })
        addr1 = _to_python({
            'formatted_address': 'test0',
            'address_components': [
                {
                    'types': ['country'],
                    'short_name': 'AU',
                    'long_name': 'Australia',
                },
                {
                    'types': ['street_address'],
                    'short_name': '',
                    'long_name': '2 Blah Street',
                }
            ]
        })
        self.assertEqual(addr0, addr1)


#     def setUp(self):
#         self.au = Country.objects.create(name='Australia', code='AU')
#         self.uk = Country.objects.create(name='United Kingdom', code='UK')

#         self.au_vic = State.objects.create(name='Victoria', code='VIC', country=self.au)
#         self.au_tas = State.objects.create(name='Tasmania', code='TAS', country=self.au)
#         self.au_qld = State.objects.create(name='Queensland', country=self.au)
#         self.au_empty = State.objects.create(country=self.au)
#         self.uk_vic = State.objects.create(name='Victoria', code='VIC', country=self.uk)

#         self.au_vic_nco = Locality.objects.create(name='Northcote', postal_code='3070', state=self.au_vic)
#         self.au_vic_mel = Locality.objects.create(name='Melbourne', postal_code='3000', state=self.au_vic)
#         self.au_vic_ftz = Locality.objects.create(name='Fitzroy', state=self.au_vic)
#         self.au_vic_empty = Locality.objects.create(state=self.au_vic)
#         self.uk_vic_mel = Locality.objects.create(name='Melbourne', postal_code='3000', state=self.uk_vic)

#         self.ad1 = Address.objects.create(street_number='1', route='Some Street', locality=self.au_vic_mel,
#                                           raw='1 Some Street, Victoria, Melbourne')
#         self.ad2 = Address.objects.create(street_number='10', route='Other Street', locality=self.au_vic_mel,
#                                           raw='10 Other Street, Victoria, Melbourne')
#         self.ad3 = Address.objects.create(street_number='1', route='Some Street', locality=self.au_vic_nco,
#                                           raw='1 Some Street, Northcote, Victoria')
#         self.ad_empty = Address.objects.create(locality=self.au_vic_nco, raw='Northcote, Victoria')

#     def test_required_raw(self):
#         obj = Address.objects.create()
#         self.assertRaises(ValidationError, obj.clean)

#     def test_ordering(self):
#         qs = Address.objects.all()
#         self.assertEqual(qs.count(), 4)
#         self.assertEqual(qs[0].route, 'Other Street')
#         self.assertEqual(qs[1].route, 'Some Street')
#         self.assertEqual(qs[2].route, '')
#         self.assertEqual(qs[3].route, 'Some Street')

#     # def test_unique_street_address_locality(self):
#     #     Address.objects.create(street_number='10', route='Other Street', locality=self.au_vic_nco)
#     #     self.assertRaises(
#     #         IntegrityError, Address.objects.create,
#     #         street_number='10', route='Other Street', locality=self.au_vic_mel
#     #     )

#     def test_unicode(self):
#         self.assertEqual(unicode(self.ad1), u'1 Some Street, Melbourne, Victoria 3000, Australia')
#         self.assertEqual(unicode(self.ad_empty), u'Northcote, Victoria 3070, Australia')

# class AddressFieldTestCase(TestCase):

#     class TestModel(object):
#         address = AddressField()

#     def setUp(self):
#         self.ad1_dict = {
#             'raw': '1 Somewhere Street, Northcote, Victoria 3070, VIC, AU',
#             'street_number': '1',
#             'route': 'Somewhere Street',
#             'locality': 'Northcote',
#             'postal_code': '3070',
#             'state': 'Victoria',
#             'state_code': 'VIC',
#             'country': 'Australia',
#             'country_code': 'AU'
#         }
#         self.test = self.TestModel()

#     def test_assignment_from_dict(self):
#         self.test.address = to_python(self.ad1_dict)
#         self.assertEqual(self.test.address.raw, self.ad1_dict['raw'])
#         self.assertEqual(self.test.address.street_number, self.ad1_dict['street_number'])
#         self.assertEqual(self.test.address.route, self.ad1_dict['route'])
#         self.assertEqual(self.test.address.locality.name, self.ad1_dict['locality'])
#         self.assertEqual(self.test.address.locality.postal_code, self.ad1_dict['postal_code'])
#         self.assertEqual(self.test.address.locality.state.name, self.ad1_dict['state'])
#         self.assertEqual(self.test.address.locality.state.code, self.ad1_dict['state_code'])
#         self.assertEqual(self.test.address.locality.state.country.name, self.ad1_dict['country'])
#         self.assertEqual(self.test.address.locality.state.country.code, self.ad1_dict['country_code'])

#     def test_assignment_from_dict_no_country(self):
#         ad = {
#             'raw': '1 Somewhere Street, Northcote, Victoria 3070, VIC, AU',
#             'street_number': '1',
#             'route': 'Somewhere Street',
#             'locality': 'Northcote',
#             'state': 'Victoria',
#         }
#         self.test.address = to_python(ad)
#         self.assertEqual(self.test.address.raw, ad['raw'])
#         self.assertEqual(self.test.address.street_number, '')
#         self.assertEqual(self.test.address.route, '')
#         self.assertEqual(self.test.address.locality, None)

#     def test_assignment_from_dict_no_state(self):
#         ad = {
#             'raw': 'Somewhere',
#             'locality': 'Northcote',
#             'country': 'Australia',
#         }
#         self.test.address = to_python(ad)
#         self.assertEqual(self.test.address.raw, ad['raw'])
#         self.assertEqual(self.test.address.street_number, '')
#         self.assertEqual(self.test.address.route, '')
#         self.assertEqual(self.test.address.locality, None)

#     def test_assignment_from_dict_no_locality(self):
#         ad = {
#             'raw': '1 Somewhere Street, Northcote, Victoria 3070, VIC, AU',
#             'street_number': '1',
#             'route': 'Somewhere Street',
#             'state': 'Victoria',
#             'country': 'Australia',
#         }
#         self.test.address = to_python(ad)
#         self.assertEqual(self.test.address.raw, ad['raw'])
#         self.assertEqual(self.test.address.street_number, '')
#         self.assertEqual(self.test.address.route, '')
#         self.assertEqual(self.test.address.locality, None)

#     def test_assignment_from_dict_only_address(self):
#         ad = {
#             'raw': '1 Somewhere Street, Northcote, Victoria 3070, VIC, AU',
#             'street_number': '1',
#             'route': 'Somewhere Street',
#         }
#         self.test.address = to_python(ad)
#         self.assertEqual(self.test.address.raw, ad['raw'])
#         self.assertEqual(self.test.address.street_number, ad['street_number'])
#         self.assertEqual(self.test.address.route, ad['route'])
#         self.assertEqual(self.test.address.locality, None)

#     def test_assignment_from_dict_duplicate_country_code(self):
#         ad = {
#             'raw': '1 Somewhere Street, Northcote, Victoria 3070, VIC, AU',
#             'street_number': '1',
#             'route': 'Somewhere Street',
#             'locality': 'Northcote',
#             'state': 'Victoria',
#             'country': 'Australia',
#             'country_code': 'Australia',
#         }
#         self.test.address = to_python(ad)
#         self.assertEqual(self.test.address.raw, ad['raw'])
#         self.assertEqual(self.test.address.street_number, '1')
#         self.assertEqual(self.test.address.route, 'Somewhere Street')
#         self.assertEqual(self.test.address.locality.name, 'Northcote')
#         self.assertEqual(self.test.address.locality.state.name, 'Victoria')
#         self.assertEqual(self.test.address.locality.state.country.name, 'Australia')
#         self.assertEqual(self.test.address.locality.state.country.code, '')

#     def test_assignment_from_dict_duplicate_state_code(self):
#         ad = {
#             'raw': '1 Somewhere Street, Northcote, Victoria 3070, VIC, AU',
#             'street_number': '1',
#             'route': 'Somewhere Street',
#             'locality': 'Northcote',
#             'state': 'Victoria',
#             'state_code': 'Victoria',
#             'country': 'Australia',
#         }
#         self.test.address = to_python(ad)
#         self.assertEqual(self.test.address.raw, ad['raw'])
#         self.assertEqual(self.test.address.street_number, '1')
#         self.assertEqual(self.test.address.route, 'Somewhere Street')
#         self.assertEqual(self.test.address.locality.name, 'Northcote')
#         self.assertEqual(self.test.address.locality.state.name, 'Victoria')
#         self.assertEqual(self.test.address.locality.state.code, '')
#         self.assertEqual(self.test.address.locality.state.country.name, 'Australia')

#     def test_assignment_from_dict_invalid_country_code(self):
#         ad = {
#             'raw': '1 Somewhere Street, Northcote, Victoria 3070, VIC, AU',
#             'street_number': '1',
#             'route': 'Somewhere Street',
#             'locality': 'Northcote',
#             'state': 'Victoria',
#             'country': 'Australia',
#             'country_code': 'Something else',
#         }
#         self.assertRaises(ValueError, to_python, ad)

#     def test_assignment_from_dict_invalid_state_code(self):
#         ad = {
#             'raw': '1 Somewhere Street, Northcote, Victoria 3070, VIC, AU',
#             'street_number': '1',
#             'route': 'Somewhere Street',
#             'locality': 'Northcote',
#             'state': 'Victoria',
#             'state_code': 'Something else',
#             'country': 'Australia',
#         }
#         self.assertRaises(ValueError, to_python, ad)

#     def test_assignment_from_string(self):
#         self.test.address = to_python(self.ad1_dict['raw'])
#         self.assertEqual(self.test.address.raw, self.ad1_dict['raw'])

#     # def test_save(self):
#     #     self.test.address = self.ad1_dict
#     #     self.test.save()
#     #     test = self.TestModel.objects.all()[0]
#     #     self.assertEqual(test.address.raw, self.ad1_dict['raw'])
#     #     self.assertEqual(test.address.street_number, self.ad1_dict['street_number'])
#     #     self.assertEqual(test.address.route, self.ad1_dict['route'])
#     #     self.assertEqual(test.address.locality.name, self.ad1_dict['locality'])
#     #     self.assertEqual(test.address.locality.postal_code, self.ad1_dict['postal_code'])
#     #     self.assertEqual(test.address.locality.state.name, self.ad1_dict['state'])
#     #     self.assertEqual(test.address.locality.state.code, self.ad1_dict['state_code'])
#     #     self.assertEqual(test.address.locality.state.country.name, self.ad1_dict['country'])
#     #     self.assertEqual(test.address.locality.state.country.code, self.ad1_dict['country_code'])
