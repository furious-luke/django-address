import six
from django.db import migrations, router
from geopy.geocoders import GoogleV3
from address.models import to_python
from address.utils import query_yes_no


class ConvertAddresses(migrations.RunPython):

    def geolocate(self, orig_addr):
        location = self.geolocator.geocode(orig_addr)
        if not location:
            raise Exception('Failed to convert address: %s'%repr(orig_addr))
        new_addr = location.raw['formatted_address']
        keep = True
        if orig_addr != new_addr:
            six.print_('\nConverted address does not match original: %s -- %s'%(repr(orig_addr), repr(new_addr)))
            keep = query_yes_no('Use new value?')
        if keep:
            return to_python(location.raw, None, self.address_model, self.component_model)
        else:
            return None

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if router.allow_migrate(schema_editor.connection.alias, app_label, **self.hints):
            self.geolocator = GoogleV3(timeout=60)
            self.address_model = from_state.apps.get_model('address.address')
            self.component_model = from_state.apps.get_model('address.component')
            self.code(from_state.apps, schema_editor, self.geolocate)
