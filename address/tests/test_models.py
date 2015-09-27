from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Model
from django.conf import settings
from address.models import *
from address.models import to_python

def au_factory():
    Component.objects.create(kind=Component.KIND_COUNTRY, long_name='Australia', short_name='AU')
    Component.objects.create(kind=Component.KIND_AAL1 | Component.KIND_POLITICAL, long_name='Victoria', short_name='Vic')
    Component.objects.create(kind=Component.KIND_AAL1, long_name='Tasmania', short_name='Tas')

def nz_factory():
    return Component.objects.create(kind=Component.KIND_COUNTRY, long_name='New Zealand', short_name='NZ')

class ComponentTestCase(TestCase):

    def test_unique_constraint(self):
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            au_factory()
            self.assertRaises(IntegrityError, au_factory)
            nz_factory()
            self.assertRaises(IntegrityError, nz_factory)

    def test_filter_kind_on_country(self):
        au_factory()
        res = [r.long_name for r in Component.filter_kind(Component.objects, Component.KIND_COUNTRY)]
        self.assertEqual(res, ['Australia'])

    def test_filter_kind_on_aal1(self):
        au_factory()
        res = [r.long_name for r in Component.filter_kind(Component.objects, Component.KIND_AAL1)]
        self.assertEqual(res, ['Victoria', 'Tasmania'])

    def test_filter_kind_on_political(self):
        au_factory()
        res = [r.long_name for r in Component.filter_kind(Component.objects, Component.KIND_POLITICAL)]
        self.assertEqual(res, ['Victoria'])

    def test_get_geocode_entry(self):
        au_factory()
        vic = Component.objects.get(long_name='Victoria')
        self.assertEqual(vic.get_geocode_entry(), {
            'long_name': 'Victoria',
            'short_name': 'Vic',
            'types': ['political', 'administrative_area_level_1'],
        })

# class AddressTestCase(TestCase):

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
