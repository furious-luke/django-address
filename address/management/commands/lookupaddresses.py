from django.core.management.base import BaseCommand, CommandError

from address.models import Address


class Command(BaseCommand):
    help = 'Lookup addresses'

    def handle(self, *args, **options):
        for addr in Address.objects.all():
            if not addr.components.exists():
                new_addr = Address.to_python(addr.raw, instance=addr)
