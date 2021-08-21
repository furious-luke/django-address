from django.test import TestCase
from django.forms import ValidationError, Form
from address.forms import AddressField, AddressWidget


class TestForm(Form):
    address = AddressField()


class AddressFieldTestCase(TestCase):

    def setUp(self):
        self.form = TestForm()
        self.field = self.form.base_fields['address']
        self.missing_state = {
            'country': 'UK',
            'locality': 'Somewhere',
            'postal_code': '34904',
            'route': 'A street?',
            'street_number': '3',
            'raw': '3 A street?, Somewhere, UK',
        }

    def test_to_python_none(self):
        self.assertEqual(self.field.to_python(None), None)

    def test_to_python_empty(self):
        self.assertEqual(self.field.to_python(''), None)

    def test_to_python_invalid_lat_lng(self):
        self.assertRaises(ValidationError, self.field.to_python, {'latitude': 'x'})
        self.assertRaises(ValidationError, self.field.to_python, {'longitude': 'x'})

    def test_to_python_invalid_empty_lat_lng(self):
        self.assertEqual(self.field.to_python({'latitude': ''}), None)
        self.assertEqual(self.field.to_python({'longitude': ''}), None)

    def test_to_python_no_locality(self):
        input = {
            'country': 'United States',
            'country_code': 'US',
            'state': 'New York',
            'state_code': 'NY',
            'locality': '',
            'sublocality': 'Brooklyn',
            'postal_code': '11201',
            'route': 'Joralemon St',
            'street_number': '209',
            'raw': '209 Joralemon Street, Brooklyn, NY, United States'
        }
        res = self.field.to_python(input)
        self.assertEqual(res.locality.name, 'Brooklyn')

    def test_to_python_postal_town(self):
        '''UK addresses with no `locality`, but a populated `postal_town`, should use the
        `postal_town` as the `locality`'''
        data = {
            'raw': 'High Street, Leamington Spa',
            'route': 'High Street',
            'postal_town': 'Leamington Spa',
            'state': 'England',
            'state_code': 'England',
            'country': 'United Kingdom',
            'country_code': 'GB',
            'postal_code': 'CV31',
            'formatted': 'High St, Royal Leamington Spa, Leamington Spa CV31, UK'
        }
        address = self.field.to_python(data)
        self.assertIsNotNone(address.locality)
        self.assertEqual(address.locality.name, data["postal_town"])

    # TODO: Fix
    # def test_to_python_empty_state(self):
    #     val = self.field.to_python(self.missing_state)
    #     self.assertTrue(isinstance(val, Address))
    #     self.assertNotEqual(val.locality, None)

    def test_to_python(self):
        res = self.field.to_python({'raw': 'Someplace'})
        self.assertEqual(res.raw, 'Someplace')

    def test_render(self):
        # TODO: Check return value.
        self.form.as_table()


class AddressWidgetTestCase(TestCase):

    def test_attributes_set_correctly(self):
        wid = AddressWidget(attrs={'size': '150'})
        self.assertEqual(wid.attrs['size'], '150')
        html = wid.render('test', None)
        self.assertNotEqual(html.find('size="150"'), -1)
