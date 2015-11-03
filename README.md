# django-address


## Description

Version 2 is substantially different to version 1. Originally I'd hoped to be
able to keep the hierarchy of address components simple, with only countries,
states, localities, and street addresses. It has become quite clear that this
will not be possible for international addressing. To cope with the vast
differences in address structures `django-address` now uses a dynamic
system for constructing hierarchies based on Google's representation of any
given address.


## Requirements

 * Python 2.7+/3+
 * Django 1.8+
 * geopy
 * six

`jquery.geocomplete` is also used, but a modified version that passes back
the raw Google geocode results is supplied.


## Installation

Installation can be done manually with:

```bash
python setup.py install
```

or using `pip`:

```bash
pip install django-address
```

Then, add `address` to your `INSTALLED_APPS` list in `settings.py`:

```python
INSTALLED_APPS = (
    ...
    'address',
)
```


## Migrating Data

Migrating from version 1 to version 2 should be handled automatically. All address models
will keep their current primary-keys and each address is checked to confirm that the formatted
address matches from the original to the new version. However, *I would strongly recommend
backing everything up before migrating to the new version*.

A migration operation is provided to assist in migrating arbitrary address data to `django-address`.
Please see the example in `examples/migrate_existing.py` to see a fictional example of how
to go about converting your existing addresses.


## The Model

There are two main elements to the address model: the `Address` model and the `Component` model.

`Component` refers to an instance of any of the address component types returned by a Google
geocoding. Some examples include locality, country, street address, political boundaries, and
postal codes. Components are organised into hierarchies reflecting the natural structure of
addresses. For example, administrative boundaries are contained within a country, and neighborhoods
are contained within administrative boundaries.

`Address` refers to a unique address, and is given a formatted name, a latitude and longitude, and
a list of root `Component`s.


## The Hierarchy

One of the trickier problems is deciding what hierarchy to apply to the types Google uses
to classify addresses. The current hierarchy looks like this:

TODO: Generate a diagram of the hierarchy.

I understand that this hierarchy will probably need to be tweaked to properly cover all the
various international addressing schemes, so please feel free to open tickets or make
pull-requests if you should find such a case.


## Usage

### Address Field

To simplify storage and access of addresses, a subclass of `ForeignKey` named
`AddressField` has been created. It provides an easy method for setting new
addresses.

It can be created using the same optional arguments as a ForeignKey field.
For example:

```python
  from address.models import AddressField

  class MyModel(models.Model):
    address1 = AddressField()
    address2 = AddressField(related_name='+', blank=True, null=True)
```

Values can be set either by assigning an Address object:

```python
  obj = MyModel()
  addr = Address(...)
  obj.address1 = addr
```

By supplying a string:

```python
  obj = MyModel()
  obj.address1 = '180 Collins Street, Melbourne, Australia'
```

By supplying a primary-key (as an integer):

```python
  obj = MyModel()
  obj.address1 = 2
```

Or by supplying a dictionary representing a Google geocode:

```python
  obj = MyModel()
  obj.address = {'formatted_address': ..., 'components': [...]}
```

Please see the Google documentation for the structure of a geocoded
location.

Note: Please note that when supplying a string to an address the system
will attempt to geocode it via Google's service. This is not always possible,
for example when internet connectivity is down, or if the source of the query
has exceeded the throttling limit provided by Google. In such cases the
formatted address will be set to the string value and the components left
empty, you will need to run the `lookupaddresses` management command at such
time when the geolocation issue is resolved to lookup the empty components.

When accessed, the address field simply returns an Address object. This way
all components may be accessed naturally through the object. For example::

```python
  obj = MyModel()
  obj.address1 = '180 Collins St, Melbourne, Australia'
  print(obj.address1.formatted)
  print(obj.address1.components)
```

Root components may be accessed via the `components` many-to-many attribute,
and a flattened array of components may be accessed via the `get_components`
method.

The hierarchy of components can be traversed manually by accessing the root
components from an address and then using the `parent` attribute of each
component to move to the next level in the hierarchy. Alternatively there is
a method, `filter_kind` on both the `Address` model and the `Component` model to search
for a component type in all ancestors::

```python
  obj = MyModel()
  obj.address1 = '180 Collins St, Melbourne, Australia'
  print(obj.address1.filter_kind(KIND_COUNTRY)
  print(obj.address1.components.all()[0].filter_kind(KIND_NEIGHBORHOOD)
```

In addition, a specific component level can be extracted from an address.
Levels are defined such that the country of an address is considered level
0, the child components of a country are considered level 1, and so on.
So, to extract the state level component of an Australian address, one
could use:

```python
  obj = MyModel()
  obj.address1 = '180 Collins St, Melbourne, Australia'
  states = obj.address1.filter_level(1)
```

Bear in mind that `filter_level` will return a list of matches, as there
is no guarantee there will be only one component per level.

A list of all available component types is available in `address/kinds.py`.


## Forms

Included is a form field for simplifying address entry. A Google maps
auto-complete is performed in the browser and passed to the view. If
the lookup fails the raw entered value is stored as the `formatted`
attribute of the address. The user is responsible for correcting the address
either manually, or by using the management commands to perform a second
lookup.

### Partial Example

The model:

```python
from address.models import AddressField

class Person(models.Model):
  address = AddressField()
```

The form:

```
from address.forms import AddressField

class PersonForm(forms.Form):
  address = AddressField()
```

The template:

```html
<head>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
  {{ form.media }} <!-- needed for JS/GoogleMaps lookup -->
</head>
<body>
  {{ form }}
</body>
```
