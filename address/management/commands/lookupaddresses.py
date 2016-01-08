from django.core.management.base import BaseCommand, CommandError

from address.models import Address


class Command(BaseCommand):
    help = 'Lookup addresses'

    def handle(self, *args, **options):
        for addr in Address.objects.all():
            if not addr.components.exists():
                new_addr = Address.to_python(addr.formatted)
                addr.height = new_addr.height
                addr.latitude = new_addr.latitude
                addr.longitude = new_addr.longitude
                addr.components = new_addr.components.all()
                addr.formatted = new_addr.formatted
                addr.save()
                new_addr.delete()
