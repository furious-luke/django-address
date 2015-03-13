from django import forms
from address.forms import AddressField

class ExampleForm(forms.Form):
    address = AddressField()
