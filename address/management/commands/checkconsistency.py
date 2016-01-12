from django.core.management.base import BaseCommand, CommandError

from address.models import Address
from address.consistency import get_consistency


class Command(BaseCommand):
    help = 'Check address consistency'

    def handle(self, *args, **options):
        for addr in Address.objects.all():
            addr.consistent = get_consistency(addr)
            addr.save()
