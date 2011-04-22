from django.db import models
from django.core.exceptions import ValidationError
from conv import to_address, GoogleMapsError


class Country(models.Model):
    name = models.CharField(max_length=40, unique=True)
    code = models.CharField(max_length=2, unique=True, primary_key=True)

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s'%self.name


class State(models.Model):
    name = models.CharField(max_length=165, blank=True)
    code = models.CharField(max_length=3, blank=True)
    country = models.ForeignKey(Country, related_name='states')

    class Meta:
        unique_together = ('name', 'country')
        ordering = ('country', 'name')

    def __unicode__(self):
        txt = ''
        if self.name:
            txt += u'%s, '%self.name
        txt += unicode(self.country)
        return txt


class Locality(models.Model):
    name = models.CharField(max_length=165, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    state = models.ForeignKey(State, related_name='localities')

    class Meta:
        verbose_name_plural = 'Localities'
        unique_together = ('name', 'state')
        ordering = ('state', 'name')

    def __unicode__(self):
        txt = ''
        if self.name:
            txt = u'%s, '%self.name
            if self.postal_code:
                txt += u'%s, '%self.postal_code
        txt += unicode(self.state)
        return txt


class Address(models.Model):
    street_address = models.CharField(max_length=100, blank=True)
    locality = models.ForeignKey(Locality, related_name='addresses')

    class Meta:
        verbose_name_plural = 'Addresses'
        unique_together = ('street_address', 'locality')
        ordering = ('locality', 'street_address')

    def __unicode__(self):
        txt = ''
        if self.street_address:
            txt += u'%s, '%self.street_address
        txt += unicode(self.locality)
        return txt


class AddressField(models.ForeignKey):
    __metaclass__ = models.SubfieldBase
    description = 'An address'

    def __init__(self, **kwargs):
        super(AddressField, self).__init__(Address, **kwargs)

    def str_to_dict(self, value):
        if value is None:
            return None

        # Check for a string not conforming to the serialised format.
        if isinstance(value, basestring):
            # TODO: Check for serialised version.
            # Convert to a tuple for the next part.
            value = (value,)

        # Check if we have a tuple first, because we will convert it to a dictionary
        # and let the dictionary handler deal with it.
        if isinstance(value, tuple) and len(value) >= 1:

            # Extract our name and address.
            if len(value) >= 2:
                name = value[0]
                address = value[1]
            else:
                name = None
                address = value[0]

            # Convert to a dictionary value.
            if name:
                try:
                    value = to_address(name + ' near ' + address)
                except GoogleMapsError:
                    name = None
            if not name:
                value = to_address(address)

        return value

    def to_python(self, value):
        value = self.str_to_dict(value)
        if value is None:
            return None

        # Is it already an address object?
        if isinstance(value, Address):
            return value

        # A dictionary of named address components.
        elif isinstance(value, dict):
            country = value.get('country', '')
            country_code = value.get('country_code', '')
            state = value.get('state', '')
            state_code = value.get('state_code', '')
            locality = value.get('locality', '')
            postal_code = value.get('postal_code', '')
            street_address = value.get('street_address', '')

            # Handle the country.
            if not country:
                raise TypeError('Must have a country name.')
            try:
                country_obj = Country.objects.get(name=country)
            except Country.DoesNotExist:
                country_obj = Country(name=country, code=country_code)

            # Handle the state.
            try:
                state_obj = State.objects.get(name=state, country=country_obj)
            except State.DoesNotExist:
                state_obj = State(name=state, code=state_code, country=country_obj)

            # Handle the locality.
            try:
                locality_obj = Locality.objects.get(name=locality, state=state_obj)
            except Locality.DoesNotExist:
                locality_obj = Locality(name=locality, postal_code=postal_code, state=state_obj)

            # Handle the address.
            try:
                address_obj = Address.objects.get(street_address=street_address, locality=locality_obj)
            except Address.DoesNotExist:
                address_obj = Address(street_address=street_address, locality=locality_obj)

            # Done.
            return address_obj

        # Try to deserialise a string ... how?
        raise ValidationError('Invalid locality value')

    def pre_save(self, model_instance, add):
        address = getattr(model_instance, self.name)
        if address is None:
            return address
        address.locality.state.country.save()
        address.locality.state.save()
        address.locality.state_id = address.locality.state.pk
        address.locality.save()
        address.locality_id = address.locality.pk
        address.save()
        return address.pk
