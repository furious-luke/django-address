import json
from django.views.generic import TemplateView
from django.conf import settings


class AddressJS(TemplateView):
    content_type = "text/javascript"
    template_name = "address/address.js"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        address_settings = getattr(settings, "ADDRESS_SETTINGS", {})
        context["address_settings"] = json.dumps(address_settings)
        return context
