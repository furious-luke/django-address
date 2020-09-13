# Django Address 

**Django models for storing and retrieving postal addresses.** 

---

# Overview
Django Address is a set of models and methods for working with postal addresses.

# Requirements
 * Python (3.5, 3.6, 3.7, 3.8)
 * Django (2.2, 3.0)

We **recommend** and only officially support the latest patch release of each Python and Django series. 

# Installation
For more detailed instructions, [view the Readme for the example site](https://github.com/furious-luke/django-address/blob/master/example_site/README.md) included with this package.

```bash
pip install django-address
```

Then, add `address` to your `INSTALLED_APPS` list in `settings.py`:

```
INSTALLED_APPS = [
    # ... 
    'address',
    # ... 
]
```

You can either store your Google API key in an environment variable as `GOOGLE_API_KEY` or you can
 specify the key in `settings.py`. If you have an environment variable set it will override what you put in settings.py.
 For more information, including enabling the Google Places API, refer to [the example site](https://github.com/furious-luke/django-address/blob/master/example_site/README.md).
 
```
GOOGLE_API_KEY = 'AIzaSyD--your-google-maps-key-SjQBE'
```

# The Model

The rationale behind the model structure is centered on trying to make
it easy to enter addresses that may be poorly defined. The model field included
uses Google Maps API v3 (via the nicely done [geocomplete jquery plugin](http://ubilabs.github.io/geocomplete/)) to
determine a proper address where possible. However if this isn't possible the
raw address is used and the user is responsible for breaking the address down
into components.

It's currently assumed any address is represent-able using four components:
country, state, locality and street address. In addition, country code, state
code and postal code may be stored, if they exist.

There are four Django models used:

```
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
    raw
    street_number
    route
    locality -> Locality
```

# Address Field

To simplify storage and access of addresses, a subclass of `ForeignKey` named
`AddressField` has been created. It provides an easy method for setting new
addresses.

## ON_DELETE behavior of Address Field

By default, if you delete an Address that is related to another object, 
Django's [cascade behavior](https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.ForeignKey.on_delete) 
is used. This means the related object will also be deleted. You may also choose
to set `null=True` when defining an address field to have the address set
to Null instead of deleting the related object. For more information and an example,
see the readme for the `django-address` example_site.
 
## Creation

It can be created using the same optional arguments as a ForeignKey field.
For example:

```python
  from address.models import AddressField

  class MyModel(models.Model):
    address1 = AddressField()
    address2 = AddressField(related_name='+', blank=True, null=True)
```

## Setting Values

Values can be set either by assigning an Address object:

```python
  addr = Address(...)
  addr.save()
  obj.address = addr
```

Or by supplying a dictionary of address components:

```python
  obj.address = {'street_number': '1', 'route': 'Somewhere Ave', ...}
```

The structure of the address components is as follows:

```python
  {
    'raw': '1 Somewhere Ave, Northcote, VIC 3070, AU',
    'street_number': '1',
    'route': 'Somewhere Ave',
    'locality': 'Northcote',
    'postal_code': '3070',
    'state': 'Victoria',
    'state_code': 'VIC',
    'country': 'Australia',
    'country_code': 'AU'
  }
```

All except the `raw` field can be omitted. In addition, a raw address may
be set directly:

```python
obj.address = 'Out the back of 1 Somewhere Ave, Northcote, Australia'
```

## Getting Values

When accessed, the address field simply returns an Address object. This way
all components may be accessed naturally through the object. For example::

```python
  route = obj.address.route
  state_name = obj.address.locality.state.name
```

## Forms

Included is a form field for simplifying address entry. A Google maps
auto-complete is performed in the browser and passed to the view. If
the lookup fails the raw entered value is used.

TODO: Talk about this more.

## Partial Example

The model:

```python
from address.models import AddressField

class Person(models.Model):
  address = AddressField(on_delete=models.CASCADE)
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
{{ form.media }} <!-- needed for JS/GoogleMaps lookup -->
</head>
<body>
  {{ form }}
</body>
```

## Running Django-Address Tests
Django-address currently has partial form and model test coverage using `django.test.TestCase`.

To run the current tests:

 1. [Clone](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) `django-address` locally.
 1. Navigate to the example site, . `/django-address/example_site`
 1. Create a [virtual environment](https://www.tangowithdjango.com/book17/chapters/requirements.html#virtual-environments) and install the example site dependencies. For example:
 
    ```
    mkvirtualenv -p python3 django-address
    pip install -r requirements.txt
    ```
 1. Run `./manage.py test`

## Important note regarding US Territories
Django-address does not currently support the parsing of US territories aka Protectorates such as Guam or Puerto Rico.

This topic is under active consideration and its status is described in [#82](https://github.com/furious-luke/django-address/issues/82)
 
## Project Status Notes

This library was created by [Luke Hodkinson](@furious-luke) originally focused on Australian addresses.

In 2015 Luke began working to abstract the project so it could handle a wider variety of international addresses.

This became the current `dev` branch.  While good progress was made on this, the branch became stale and releases
continued under the current model architecture on master. 

The project is currently in open development, read more about the project status [in this issue](#98).  

If you have questions, bug reports or suggestions please create a New Issue for the project.
