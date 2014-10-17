import urllib2
from django import forms
# from uni_form.helpers import *
from django.utils.safestring import mark_safe
from djangoutils.conv import to_address
from googlemaps import GoogleMapsError
from models import get_or_create_address

import logging
logger = logging.getLogger(__name__)

__all__ = ['AddressWidget', 'AddressField']

class AddressWidget(forms.TextInput):
    components = [('country', 'country'), ('country_code', 'country_short'),
                  ('locality', 'locality'), ('postal_code', 'postal_code'),
                  ('route', 'route'), ('street_number', 'street_number'),
                  ('state', 'administrative_area_level_1'),
                  ('state_code', 'administrative_area_level_1_short'),
                  ('formatted', 'formatted_address'),
                  ('latitude', 'lat'), ('longitude', 'lng')]

    class Media:
        js = ('js/jquery.geocomplete.min.js', 'address/js/address.js')

    def render(self, name, value, attrs=None, **kwargs):

        # Can accept None, a dictionary of values or an Address object.
        if value is None:
            ad = {}
        elif isinstance(value, dict):
            ad = value
        else:
            ad = value.as_dict()

        # Generate the elements. We should create a suite of hidden fields
        # for each individual component, and a visible field for the raw
        # input. Begin by generating the raw input.
        elems = [super(AddressWidget, self).render(name, ad.get('formatted', None), attrs, **kwargs)]

        # Now add the hidden fields.
        elems.append('<div id="%s_components">'%name)
        for com in self.components:
            elems.append('<input type="hidden" name="%s_%s" data-geo="%s" value="%s" />'%(
                name, com[0], com[1], ad.get(com[0], ''))
            )
        elems.append('</div>')

        return mark_safe(unicode('\n'.join(elems)))

    def value_from_datadict(self, data, files, name):
        ad = dict([(c[0], data.get(name + '_' + c[0], '')) for c in self.components])
        return ad


class AddressField(forms.CharField):
    widget = AddressWidget

    def __init__(self, **kwargs):
        for f in ['limit_choices_to', 'queryset', 'to_field_name']:
            kwargs.pop(f, None)
        super(AddressField, self).__init__(**kwargs)

    def to_python(self, value):

        # Treat `None`s and empty strings as empty.
        if value is None or value == '':
            return None

        return get_or_create_address(value)

# def make_helper(form, primary_buttons, secondary_buttons=[]):
#     helper = FormHelper()

#     all_fieldset = Fieldset('', *[f.name for f in form.visible_fields()])

#     buttons = []
#     for name, text in primary_buttons:
#         btn = Submit(name, text, css_class='primaryAction')
#         # helper.add_input(btn)
#         buttons.append(btn)
#     for name, text in secondary_buttons:
#         btn = Submit(name, text, css_class='secondaryAction')
#         # helper.add_input(btn)
#         buttons.append(btn)
#     button_holder = ButtonHolder(*buttons)

#     layout = Layout(all_fieldset, button_holder)

# #    helper.form_action = ''
#     helper.form_method = 'POST'
#     helper.form_style = 'inline'
#     helper.add_layout(layout)
#     return helper


# class UniFormMedia(object):

#     class Media:
#         css = {'all': ('uni_form/uni-form.css', 'uni_form/default.uni-form.css')}
#         js = ('js/jquery.min.js', 'uni_form/uni-form.jquery.js')


# class TestForm(forms.Form, UniFormMedia):
#     address_full = AddressField()
#     address_no_postal_code = AddressField(widget=AddressWidget(use_postal_code=False))
#     address_no_lat_lng = AddressField(widget=AddressWidget(use_lat_lng=False))
#     address_no_codes = AddressField(widget=AddressWidget(use_codes=False))
#     address_minimal = AddressField(widget=AddressWidget(use_postal_code=False, use_lat_lng=False, use_codes=False))

#     @property
#     def helper(self):
#         return make_helper(self, (('okay', 'Okay'),), (('cancel', 'Cancel'),))
