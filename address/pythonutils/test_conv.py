from unittest import TestCase
import conv


class ToAddressTestCase(TestCase):

    # Replace with your key.
    API_KEY = 'ABQIAAAAaI_gcekITBRIeNw8z-0BhRT2yXp_ZAY8_ufC3CFXhHIE1NvwkxTpJRa5QCuoj_D2SvGNPvZcy0xiCg'

    def test_none(self):
        value = conv.to_address(None, None)
        self.assertEquals(value, None)

    def test_latlng_floats(self):
        latlng = (-37.8131869, 144.9629796)
        value = conv.to_address(latlng, self.API_KEY)
        self.assertEquals(value['country'], 'Australia')

    def test_latlng_ints(self):
        latlng = (-37, 144)
        value = conv.to_address(latlng, self.API_KEY)
        self.assertEquals(value['country'], 'Australia')

    def test_landmark(self):
        place = ('cherry bar', 'melbourne, australia')
        value = conv.to_address(place, self.API_KEY)
        self.assertEquals(value['country'], 'Australia')

    def test_address(self):
        value = conv.to_address('melbourne, australia', self.API_KEY)
        self.assertEquals(value['country'], 'Australia')
