from django.test import TestCase
from django.db import IntegrityError
from django.db.models import Model
import models


class CountryTestCase(TestCase):

    def setUp(self):
        self.au = models.Country.objects.create(name='Australia', code='AU')
        self.nz = models.Country.objects.create(name='New Zealand', code='NZ')
        self.be = models.Country.objects.create(name='Belgium', code='BE')

    def test_required_name(self):
        self.assertRaises(IntegrityError, models.Country.objects.create, code='BL')

    def test_required_code(self):
        self.assertRaises(IntegrityError, models.Country.objects.create, name='Blah')

    def test_ordering(self):
        qs = models.Country.objects.all()
        self.assertEqual(qs.count(), 3)
        self.assertEqual(qs[0].code, 'AU')
        self.assertEqual(qs[1].code, 'BE')
        self.assertEqual(qs[2].code, 'NZ')

    def test_unique_name(self):
        self.assertRaises(IntegrityError, models.Country.objects.create, name='Australia', code='**')

    def test_unicode(self):
        self.assertEqual(unicode(self.au), u'Australia')


class StateTestCase(TestCase):

    def setUp(self):
        self.au = models.Country.objects.create(name='Australia', code='AU')
        self.vic = models.State.objects.create(name='Victoria', code='VIC', country=self.au)
        self.tas = models.State.objects.create(name='Tasmania', code='TAS', country=self.au)
        self.qld = models.State.objects.create(name='Queensland', country=self.au)
        self.empty = models.State.objects.create(country=self.au)
        self.uk = models.Country.objects.create(name='United Kingdom', code='UK')
        self.uk_vic = models.State.objects.create(name='Victoria', code='VIC', country=self.uk)

    def test_required_country(self):
        self.assertRaises(IntegrityError, models.State.objects.create)

    def test_ordering(self):
        qs = models.State.objects.all()
        self.assertEqual(qs.count(), 5)
        self.assertEqual(qs[0].name, '')
        self.assertEqual(qs[1].name, 'Queensland')
        self.assertEqual(qs[2].name, 'Tasmania')
        self.assertEqual(qs[3].name, 'Victoria')
        self.assertEqual(qs[4].name, 'Victoria')

    def test_unique_name_country(self):
        models.State.objects.create(name='Tasmania', country=self.uk)
        self.assertRaises(IntegrityError, models.State.objects.create, name='Tasmania', country=self.au)

    def test_unicode(self):
        self.assertEqual(unicode(self.vic), u'Victoria, Australia')
        self.assertEqual(unicode(self.empty), u'Australia')


class LocalityTestCase(TestCase):

    def setUp(self):
        self.au = models.Country.objects.create(name='Australia', code='AU')
        self.uk = models.Country.objects.create(name='United Kingdom', code='UK')

        self.au_vic = models.State.objects.create(name='Victoria', code='VIC', country=self.au)
        self.au_tas = models.State.objects.create(name='Tasmania', code='TAS', country=self.au)
        self.au_qld = models.State.objects.create(name='Queensland', country=self.au)
        self.au_empty = models.State.objects.create(country=self.au)
        self.uk_vic = models.State.objects.create(name='Victoria', code='VIC', country=self.uk)

        self.au_vic_nco = models.Locality.objects.create(name='Northcote', postal_code='3070', state=self.au_vic)
        self.au_vic_mel = models.Locality.objects.create(name='Melbourne', postal_code='3000', state=self.au_vic)
        self.au_vic_ftz = models.Locality.objects.create(name='Fitzroy', state=self.au_vic)
        self.au_vic_empty = models.Locality.objects.create(state=self.au_vic)
        self.uk_vic_mel = models.Locality.objects.create(name='Melbourne', postal_code='3000', state=self.uk_vic)

    def test_required_state(self):
        self.assertRaises(IntegrityError, models.Locality.objects.create)

    def test_ordering(self):
        qs = models.Locality.objects.all()
        self.assertEqual(qs.count(), 5)
        self.assertEqual(qs[0].name, '')
        self.assertEqual(qs[1].name, 'Fitzroy')
        self.assertEqual(qs[2].name, 'Melbourne')
        self.assertEqual(qs[3].name, 'Northcote')
        self.assertEqual(qs[4].name, 'Melbourne')

    def test_unique_name_state(self):
        models.Locality.objects.create(name='Melbourne', state=self.au_qld)
        self.assertRaises(IntegrityError, models.Locality.objects.create, name='Melbourne', state=self.au_vic)

    def test_unicode(self):
        self.assertEqual(unicode(self.au_vic_mel), u'Melbourne, 3000, Victoria, Australia')
        self.assertEqual(unicode(self.au_vic_ftz), u'Fitzroy, Victoria, Australia')
        self.assertEqual(unicode(self.au_vic_empty), u'Victoria, Australia')


class AddressTestCase(TestCase):

    def setUp(self):
        self.au = models.Country.objects.create(name='Australia', code='AU')
        self.uk = models.Country.objects.create(name='United Kingdom', code='UK')

        self.au_vic = models.State.objects.create(name='Victoria', code='VIC', country=self.au)
        self.au_tas = models.State.objects.create(name='Tasmania', code='TAS', country=self.au)
        self.au_qld = models.State.objects.create(name='Queensland', country=self.au)
        self.au_empty = models.State.objects.create(country=self.au)
        self.uk_vic = models.State.objects.create(name='Victoria', code='VIC', country=self.uk)

        self.au_vic_nco = models.Locality.objects.create(name='Northcote', postal_code='3070', state=self.au_vic)
        self.au_vic_mel = models.Locality.objects.create(name='Melbourne', postal_code='3000', state=self.au_vic)
        self.au_vic_ftz = models.Locality.objects.create(name='Fitzroy', state=self.au_vic)
        self.au_vic_empty = models.Locality.objects.create(state=self.au_vic)
        self.uk_vic_mel = models.Locality.objects.create(name='Melbourne', postal_code='3000', state=self.uk_vic)

        self.ad1 = models.Address.objects.create(street_address='1 Some Street', locality=self.au_vic_mel)
        self.ad2 = models.Address.objects.create(street_address='10 Other Street', locality=self.au_vic_mel)
        self.ad3 = models.Address.objects.create(street_address='1 Some Street', locality=self.au_vic_nco)
        self.ad_empty = models.Address.objects.create(locality=self.au_vic_nco)

    def test_required_locality(self):
        self.assertRaises(IntegrityError, models.Address.objects.create)

    def test_ordering(self):
        qs = models.Address.objects.all()
        self.assertEqual(qs.count(), 4)
        self.assertEqual(qs[0].street_address, '1 Some Street')
        self.assertEqual(qs[1].street_address, '10 Other Street')
        self.assertEqual(qs[2].street_address, '')
        self.assertEqual(qs[3].street_address, '1 Some Street')


    def test_unique_street_address_locality(self):
        models.Address.objects.create(street_address='10 Other Street', locality=self.au_vic_nco)
        self.assertRaises(
            IntegrityError, models.Address.objects.create,
            street_address='10 Other Street', locality=self.au_vic_mel
        )

    def test_unicode(self):
        self.assertEqual(unicode(self.ad1), u'1 Some Street, Melbourne, 3000, Victoria, Australia')
        self.assertEqual(unicode(self.ad_empty), u'Northcote, 3070, Victoria, Australia')


class AddressFieldTestCase(TestCase):

    class TestModel(Model):
        address = models.AddressField()

    def setUp(self):
        self.ad1_dict = {
            'street_address': '1 Somewhere Street',
            'locality': 'Northcote',
            'postal_code': '3070',
            'state': 'Victoria',
            'state_code': 'VIC',
            'country': 'Australia',
            'country_code': 'AU'
        }
        self.test = self.TestModel()

    def test_assignment_from_dict(self):
        self.test.address = self.ad1_dict
        self.assertEqual(self.test.address.street_address, self.ad1_dict['street_address'])
        self.assertEqual(self.test.address.locality.name, self.ad1_dict['locality'])
        self.assertEqual(self.test.address.locality.postal_code, self.ad1_dict['postal_code'])
        self.assertEqual(self.test.address.locality.state.name, self.ad1_dict['state'])
        self.assertEqual(self.test.address.locality.state.code, self.ad1_dict['state_code'])
        self.assertEqual(self.test.address.locality.state.country.name, self.ad1_dict['country'])
        self.assertEqual(self.test.address.locality.state.country.code, self.ad1_dict['country_code'])

    def test_assignment_from_tuple(self):
        self.test.address = ('110 Swanston Street, Melbourne, Australia',)
        self.assertEqual(self.test.address.street_address, '110 Swanston St')
        self.assertEqual(self.test.address.locality.name, 'Melbourne')
        self.assertEqual(self.test.address.locality.postal_code, '3000')
        self.assertEqual(self.test.address.locality.state.name, 'VIC')
        self.assertEqual(self.test.address.locality.state.country.name, 'Australia')
        self.assertEqual(self.test.address.locality.state.country.code, 'AU')

    def test_assignment_from_tuple_with_name(self):
        self.test.address = ('cherry', '103 Flinders Lane, Melbourne, Australia')
        self.assertEqual(self.test.address.street_address, '103 Flinders Ln')
        self.assertEqual(self.test.address.locality.name, 'Melbourne')
        self.assertEqual(self.test.address.locality.postal_code, '3000')
        self.assertEqual(self.test.address.locality.state.name, 'VIC')
        self.assertEqual(self.test.address.locality.state.country.name, 'Australia')
        self.assertEqual(self.test.address.locality.state.country.code, 'AU')

    def test_save(self):
        self.test.address = self.ad1_dict
        self.test.save()
        test = self.TestModel.objects.all()[0]
        self.assertEqual(test.address.street_address, self.ad1_dict['street_address'])
        self.assertEqual(test.address.locality.name, self.ad1_dict['locality'])
        self.assertEqual(test.address.locality.postal_code, self.ad1_dict['postal_code'])
        self.assertEqual(test.address.locality.state.name, self.ad1_dict['state'])
        self.assertEqual(test.address.locality.state.code, self.ad1_dict['state_code'])
        self.assertEqual(test.address.locality.state.country.name, self.ad1_dict['country'])
        self.assertEqual(test.address.locality.state.country.code, self.ad1_dict['country_code'])
