from django import forms
from uni_form.helpers import *
from django.utils.safestring import mark_safe
from models import get_or_create_address

import logging
logger = logging.getLogger(__name__)


__all__ = ['AddressWidget', 'AddressField']


class AddressWidget(forms.Textarea):

    # class Media:
    #     js = ('js/jquery.min.js', 'address/js/address.js',)

    def __init__(self, *args, **kwargs):
        self._use_postal_code = kwargs.pop('use_postal_code', True)
        self._use_lat_lng = kwargs.pop('use_lat_lng', True)
        self._use_codes = kwargs.pop('use_codes', True)
        super(AddressWidget, self).__init__(*args, **kwargs)

    def _get_value(self, ad, com):
        val = ad.get(com, '')
        if val is None:
            val = ''
        return val

    def render(self, name, value, attrs=None, **kwargs):

        # Can accept None, a dictionary of values or an Address object.
        if value is None:
            ad = {}
        elif isinstance(value, dict):
            ad = value
        else:
            ad = value.as_dict()

        elems = [
            '<ul>',

            # '<li><button style="margin-left:0" type="button" class="address-lookup-btn">Google lookup</button></li>',

            '<li style="width:97%%"><label>Street address<input type="text" class="textinput textInput" id="id_address-street_address" name="address-street_address" value="%s" /></label></li>'%self._get_value(ad, 'street_address'),
        ]

        if self._use_postal_code:
            elems.extend([
                '<ul style="width:100%%" class="alternate">',
                '<li style="width:58%%"><label>Locality<input type="text" class="textinput textInput" id="id_address-locality" name="address-locality" value="%s" /></label></li>'%self._get_value(ad, 'locality'),
                '<li style="width:35%%"><label>Postal code<input type="text" class="textinput textInput" id="id_address-postal_code" name="address-postal_code" value="%s" /></label></li>'%self._get_value(ad, 'postal_code'),
                '</ul>',
            ])
        else:
            elems.extend([
                '<li style="width:97%%"><label>Locality<input type="text" class="textinput textInput" id="id_address-locality" name="address-locality" value="%s" /></label></li>'%self._get_value(ad, 'locality'),
            ])

        if self._use_codes:
            elems.extend([
                '<ul style="width:100%%" class="alternate">',
                '<li style="width:68%%"><label>State<input type="text" class="textinput textInput" id="id_address-state" name="address-state" value="%s" /></label></li>'%self._get_value(ad, 'state'),
                '<li style="width:25%%"><label>State code<input type="text" class="textinput textInput" id="id_address-state_code" name="address-state_code" value="%s" /></label></li>'%self._get_value(ad, 'state_code'),
                '</ul>',

                '<ul style="width:100%%" class="alternate">',
                '<li style="width:68%%"><label>Country<input type="text" class="textinput textInput" id="id_address-country" name="address-country" value="%s" /></label></li>'%self._get_value(ad, 'country'),
                '<li style="width:25%%"><label>Country code<input type="text" class="textinput textInput" id="id_address-country_code" name="address-country_code" value="%s" /></label></li>'%self._get_value(ad, 'country_code'),
                '</ul>',
            ])
        else:
            elems.extend([
                '<ul style="width:100%%" class="alternate">',
                '<li style="width:47%%"><label>State<input type="text" class="textinput textInput" id="id_address-state" name="address-state" value="%s" /></label></li>'%self._get_value(ad, 'state'),
                '<li style="width:46%%"><label>Country<input type="text" class="textinput textInput" id="id_address-country" name="address-country" value="%s" /></label></li>'%self._get_value(ad, 'country'),
                '</ul>',
            ])

        if self._use_lat_lng:
            elems.extend([
                '<ul style="width:100%%" class="alternate">',
                '<li style="width:47%%"><label>Latitude<input type="text" class="textinput textInput" id="id_address-latitude" name="address-latitude" value="%s" /></label></li>'%self._get_value(ad, 'latitude'),
                '<li style="width:46%%"><label>Longitude<input type="text" class="textinput textInput" id="id_address-longitude" name="address-longitude" value="%s" /></label></li>'%self._get_value(ad, 'longitude'),
                '</ul>',
            ])

        elems.extend([
            '</ul>',
        ])
        # components = ['street_address', 'locality', 'postal_code', 'state', 'state_code',
        #               'country', 'country_code', 'latitude', 'longitude']
        # for com in components:
        #     val = ad.get(com, '')
        #     if val is None:
        #         val = ''
        #     elems.extend([
        #         '<li>',
        #         '<label>%s'%com.replace('_', ' ').capitalize(),
        #         '<input type="text" class="textinput textInput" id="id_address-%s" name="address-%s" value="%s" />'%(com, com, val),
        #         '</label>',
        #         '</li>',
        #     ])
        # elems.append('</ul>')
        return mark_safe(unicode('\n'.join(elems)))

    def value_from_datadict(self, data, files, name):
        ad = dict(
            street_address=data.get('address-street_address', ''),
            locality=data.get('address-locality', ''),
            postal_code=data.get('address-postal_code', ''),
            state=data.get('address-state', ''),
            state_code=data.get('address-state_code', ''),
            country=data.get('address-country', ''),
            country_code=data.get('address-country_code', ''),
            latitude=data.get('address-latitude', ''),
            longitude=data.get('address-longitude', ''),
        )
        return ad


class AddressField(forms.Field):
    widget = AddressWidget

    def to_python(self, value):
        if value is None:
            return None
        if not value['latitude']:
            value['latitude'] = None
        else:
            try:
                value['latitude'] = float(value['latitude'])
            except ValueError:
                raise forms.ValidationError('Invalid latitude.')
        if not value['longitude']:
            value['longitude'] = None
        else:
            try:
                value['longitude'] = int(value['longitude'])
            except ValueError:
                raise forms.ValidationError('Invalid longitude.')
        return get_or_create_address(value)


def make_helper(form, primary_buttons, secondary_buttons=[]):
    helper = FormHelper()

    all_fieldset = Fieldset('', *[f.name for f in form.visible_fields()])

    buttons = []
    for name, text in primary_buttons:
        btn = Submit(name, text, css_class='primaryAction')
        # helper.add_input(btn)
        buttons.append(btn)
    for name, text in secondary_buttons:
        btn = Submit(name, text, css_class='secondaryAction')
        # helper.add_input(btn)
        buttons.append(btn)
    button_holder = ButtonHolder(*buttons)

    layout = Layout(all_fieldset, button_holder)

#    helper.form_action = ''
    helper.form_method = 'POST'
    helper.form_style = 'inline'
    helper.add_layout(layout)
    return helper


class UniFormMedia(object):

    class Media:
        css = {'all': ('uni_form/uni-form.css', 'uni_form/default.uni-form.css')}
        js = ('js/jquery.min.js', 'uni_form/uni-form.jquery.js')


class TestForm(forms.Form, UniFormMedia):
    address_full = AddressField()
    address_no_postal_code = AddressField(widget=AddressWidget(use_postal_code=False))
    address_no_lat_lng = AddressField(widget=AddressWidget(use_lat_lng=False))
    address_no_codes = AddressField(widget=AddressWidget(use_codes=False))
    address_minimal = AddressField(widget=AddressWidget(use_postal_code=False, use_lat_lng=False, use_codes=False))

    @property
    def helper(self):
        return make_helper(self, (('okay', 'Okay'),), (('cancel', 'Cancel'),))
