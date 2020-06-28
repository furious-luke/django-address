from django.db import models
from address.models import AddressField


class Person(models.Model):
    """Model definition for Person."""
    first_name = models.CharField(max_length=20, blank=True)
    address = AddressField(null=True, blank=True)

    class Meta:
        """Meta definition for Person."""

        verbose_name = 'Person'
        verbose_name_plural = 'People'

    def __str__(self):
        """Unicode representation of Person."""
        return "%s" % self.id
