from django.db.models.signals import pre_save
from django.dispatch import receiver

from address.models import Address


@receiver(pre_save, sender=Address)
def populate_formatted(_sender, instance, **_kwargs):
    """If "formatted" is empty try to construct it from other values."""
    if not instance.formatted:
        instance.formatted = str(instance)
