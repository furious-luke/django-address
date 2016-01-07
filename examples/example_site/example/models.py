from django.db import models
from address.models import AddressField

class Example(models.Model):
    address = AddressField(blank=True, null=True)
    old_address = models.CharField(max_length=1024, default='')
