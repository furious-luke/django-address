import six
from django.db import migrations, router
from django.conf import settings
from geopy.geocoders import GoogleV3
from address.models import Address #, to_python
# from address.utils import query_yes_no


class ConvertAddresses(migrations.RunPython):

    def geolocate(self, orig_addr):
        new_addr = Address.to_python(orig_addr,
                                     address_model=self.address_model,
                                     component_model=self.component_model)
        new_addr._an_unortunate_hack = True
        return new_addr
        # location = self.geolocator.geocode(orig_addr)
        # if not location:
        #     raise Exception('Failed to convert address: %s'%repr(orig_addr))
        # new_addr = location.raw['formatted_address']
        # keep = True
        # if orig_addr != new_addr:
        #     six.print_('\nConverted address does not match original: %s -- %s'%(repr(orig_addr), repr(new_addr)))
        #     keep = query_yes_no('Use new value?')
        # if keep:
        #     new_addr = to_python(location.raw, None, self.address_model, self.component_model)
        #     new_addr._an_unortunate_hack = True
        #     return new_addr
        # else:
        #     return None

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if router.allow_migrate(schema_editor.connection.alias, app_label, **self.hints):
            self.geolocator = GoogleV3(api_key=getattr(settings, 'GOOGLE_API_KEY', None), timeout=60)
            self.address_model = from_state.apps.get_model('dj_address.address')
            self.component_model = from_state.apps.get_model('dj_address.component')
            self.code(from_state.apps, schema_editor, self.geolocate)
