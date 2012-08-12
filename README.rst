==============
django-address
==============

Disclaimer
==========

These instructions are a little shabby, I havn't had a whole lot of time to
devote to explaining things thoroughly. If you're interested in using this
but are having trouble getting it setup please feel free to email me at
furious.luke@gmail.com, I'll assist as best I can and update the instructions
in the process. Cheers!

Installation
============

Uses Django 1.3, but needs to be patched using the supplied diff file,
"django-1.3.diff". This fix has been submitted to the Django team, hopefully
it will be included in the next release.

django-address depends on a couple of other repositories I use to store small
utilities:

  python-utils
    A suite of simple Python utilities.

  django-utils
    A suite of simple Django utilities.

You will need to download and install both python-utils and django-utils from
my github repositories.

Beyond that, use the provided "setup.py".

The Model
=========

It's currently assumed any address is representable using four components:
country, state, locality and street address. In addition, country code, state
code and postal code may be stored, if they exist.

There are four Django models used::

  Country
    name
    code

  State
    name
    code
    country -> Country

  Locality
    name
    postal_code
    state -> State

  Address
    street_address
    locality -> Locality

Address Field
=============

To simplify storage and access of addreses, a subclass of ForeignKey named
AddressField has been created. It provides an easy method for setting new
addresses.

Creation
--------

It can be created using the same optional arguments as a ForeignKey field.
For example::

  class MyModel(models.Model):
    address1 = AddressField()
    address2 = AddressField(blank=True, null=True)

Setting Values
--------------

Values can be set either by assigning an Address object::

  obj.address = Address.objects.create(...)

Or, more conveniently, by supplying a dictionary of address components::

  obj.address = {'street_address': '1 Somewhere Ave', ...}

The structure of the address components is as follows::

  {
    'street_address': '1 Somewhere Ave',
    'locality': 'Northcote',
    'postal_code': '3070',
    'state': 'Victoria',
    'state_code': 'VIC',
    'country': 'Australia',
    'country_code': 'AU'
  }

The only required components are ``country`` and ``country_code``. Everything
else can be safely omitted. This is mostly to allow whole regions as valid
addresses (I'm not actually too sure this is a good idea yet).

The final method for setting addresses is using a tuple of strings. If the tuple
is of length one, the only entry is taken to be an approximate address. If the
tuple is of length two or more, the first entry is taken to be the name of a
nearby landmark and the second entry is taken to be an approximate address. These
values are then used in a Google Maps lookup, the result being stored on the
field.

Getting Values
--------------

When accessed, the address field simply returns an Address object. This way
all components may be accessed naturally through the object. For example::

  street_address = obj.address.name
  state_name = obj.address.locality.state.name
