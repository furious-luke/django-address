from django import forms
from address.forms import AddressField
from .models import Person


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        address = AddressField()
        fields = "__all__"
