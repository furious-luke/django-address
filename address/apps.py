from django.apps import AppConfig


class AddressConfig(AppConfig):
    """
    Define config for the member app so that we can hook in signals.
    """

    name = "address"

    def ready(self):
        import address.signals
