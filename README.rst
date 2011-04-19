==============
django-address
==============
--------------------
Simplified addresses
--------------------

Installation
============

Uses Django 1.3, but needs to be patched using the supplied diff file,
"django-1.3.diff". This fix has been submitted to the Django team, hopefully
it will be included in the next release.

Beyond that, use the provided "setup.py".

The Model
=========

It's currently assumed any address is representable using four components:
country, state, locality and street address. In addition, country code, state
code and postal code may be stored, if they exist.

There are four Django models used: Country, State, Locality and Address.

Address Field
=============

To simplify storage and access of addreses, a subclass of ForeignKey named
AddressField has been created. It provides an easy method for setting new
addresses.

Creation
--------

It can be created using the same optional arguments as a ForeignKey field.
For example:::

  class MyModel(models.Model):
    address1 = AddressField()
    address2 = AddressField(blank=True, null=True)

Setting Values
--------------

Values can be set either by assigning an Address object:::

  obj.address = Address.objects.create(...)

Or, more conveniently, by supplying a dictionary of address components:

  obj.address = {'street_address': '1 Somewhere Ave', ...}

The structure of the address components is as follows:::

  {
    'street_address': '',
    'locality': '',
    'postal_code': '',
    'state': '',
    'state_code': '',
    'country': '',
    'country_code': ''
  }

Usage
=====

TODO
