from django import forms
from address.forms import AddressField


class PersonForm(forms.Form):
    address = AddressField()
