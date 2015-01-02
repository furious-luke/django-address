from django.test import TestCase
from django.forms import ValidationError, Form
from address.forms import AddressField

class TestForm(Form):
    address = AddressField()

class AddressFieldTestCase(TestCase):

    def setUp(self):
        self.form = TestForm()
        self.field = self.form.base_fields['address']

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

    def test_to_python(self):
        res = self.field.to_python({'raw': 'Someplace'})
        self.assertEqual(res.raw, 'Someplace')

    def test_render(self):
        html = self.form.as_table()
        # TODO: Check html
